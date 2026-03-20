import concurrent.futures
import json
import os
import tempfile
from typing import List

import cv2
import redis
import torch
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from faster_whisper import WhisperModel
from scenedetect import ContentDetector, detect

from app.ai_modules.llm.gemini_client import gemini_client
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.postgres import SessionLocal
from app.models.document import Document
from app.services.s3_svc import s3_service


class IngestionService:
    """
    Utility class for text manipulation and ML model caching.
    Kept here because other services (like GraphService) depend on it.
    """

    _whisper_model = None
    _doc_converter = None

    @classmethod
    def get_whisper_model(cls):
        if cls._whisper_model is None:
            print("[ML Cache] Initializing WhisperModel into VRAM...")
            # Dynamically detect hardware. This is safe for production (uses
            # GPU) AND safe for local testing (likely uses CPU).
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            cls._whisper_model = WhisperModel(
                "small", device=device, compute_type=compute_type
            )
        return cls._whisper_model

    @classmethod
    def get_doc_converter(cls):
        if cls._doc_converter is None:
            print("[ML Cache] Initializing Docling Converter into RAM...")
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.generate_picture_images = True
            pipeline_options.ocr_options = EasyOcrOptions(lang=["en", "vi"])
            cls._doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        return cls._doc_converter

    @staticmethod
    def chunk_text(text: str, max_words_per_chunk: int = 4000) -> List[str]:
        """
        Smart Chunking for Markdown: Splits the document primarily by Markdown headers.
        Forces a split at the nearest paragraph if a section exceeds max_words_per_chunk.
        """
        print("[IngestionService] Starting smart semantic Markdown chunking...")

        blocks = text.split("\n\n")
        chunks = []
        current_chunk_blocks = []
        current_word_count = 0

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            block_word_count = len(block.split())

            # Check if block is a Markdown header (e.g., "# Title", "## Section")
            is_title = (
                block.startswith("# ")
                or block.startswith("## ")
                or block.startswith("### ")
            )
            is_too_long = (current_word_count + block_word_count) > max_words_per_chunk

            if (is_title or is_too_long) and current_chunk_blocks:
                chunks.append("\n\n".join(current_chunk_blocks))
                current_chunk_blocks = []
                current_word_count = 0

            current_chunk_blocks.append(block)
            current_word_count += block_word_count

        if current_chunk_blocks:
            chunks.append("\n\n".join(current_chunk_blocks))

        print(f"[IngestionService] Document split into {len(chunks)} semantic chunks.")
        return chunks


redis_client = redis.from_url(settings.CELERY_BROKER_URL)


def publish_event(user_id: int, event_type: str, payload: dict):
    """Hàm bắn event về WebSocket thông qua Redis PubSub"""
    message = {"user_id": user_id, "event": event_type, "payload": payload}
    redis_client.publish("user_notifications", json.dumps(message))


@celery_app.task(bind=True, name="process_document_task")
def process_document_task(self, document_id: int, file_path: str):
    """
    Background Celery task to process PDF or Video.
    Runs in a separate worker process to avoid blocking the FastAPI server.
    """
    print(f"[Celery Worker] Started processing document ID: {document_id}")
    db = SessionLocal()

    # Fetch the pending document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        print(f"[Celery Worker] Error: Document {document_id} not found in DB.")
        db.close()
        return

    try:
        content_text = ""

        # Upload the file to S3 first
        print("[Celery Worker] Uploading file to S3...")
        s3_url = s3_service.upload_file(file_path, document.file_type)

        # Route to the correct processing logic based on file type
        if document.file_type == "pdf":
            content_text = _process_pdf_logic(file_path)
        elif document.file_type == "video":
            content_text = _process_video_logic(file_path)
        else:
            raise ValueError(f"Unsupported file type: {document.file_type}")

        # Update DB successfully
        document.content_text = content_text
        document.file_url = s3_url
        document.status = "completed"
        db.commit()
        print(f"[Celery Worker] Document {document_id} processed successfully.")

        # Shoot the Ingestion event
        publish_event(
            user_id=document.user_id,
            event_type="DOCUMENT_STATUS_UPDATED",
            payload={"document_id": document.id, "status": "completed"},
        )

    except Exception as e:
        print(f"[Celery Worker] Fatal Error processing document {document_id}: {e}")
        db.rollback()
        document.status = "failed"
        document.error_message = str(e)
        db.commit()
        publish_event(
            user_id=document.user_id,
            event_type="DOCUMENT_STATUS_UPDATED",
            payload={"document_id": document.id, "status": "failed", "error": str(e)},
        )

    finally:
        db.close()
        # Clean up local file to save disk space after processing is done
        if os.path.exists(file_path):
            os.remove(file_path)
            print(
                f"[Celery Worker] Cleaned up local temporary file: {file_path}. Backend storage remains empty."
            )


def _process_pdf_logic(file_path: str) -> str:
    print(f"[_process_pdf_logic] Running Docling on {file_path}...")

    # 1. Retrieve cached Docling Pipeline
    doc_converter = IngestionService.get_doc_converter()

    # 2. Execute Conversion
    conv_result = doc_converter.convert(file_path)
    doc = conv_result.document

    document_flow = []
    current_page = None

    # 3. Process items in reading order & parallelize Vision calls
    with tempfile.TemporaryDirectory() as temp_dir:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for item, _ in doc.iterate_items():
                # CHECK IF THE PAGE CHANGED
                page_marker = ""
                if hasattr(item, "prov") and item.prov and len(item.prov) > 0:
                    page_no = item.prov[0].page_no
                    if page_no != current_page:
                        current_page = page_no
                        # Only inject a clean header when the page turns
                        page_marker = f"\n\n--- [PAGE {current_page}] ---\n\n"

                # Duck-typing is safer than checking type(item).__name__ across Docling versions
                if hasattr(item, "get_image") and item.label == "picture":
                    # If an image is the first item on a new page, append the page marker first
                    if page_marker:
                        document_flow.append({"type": "text", "content": page_marker})

                    try:
                        pil_img = item.get_image(doc)
                        if pil_img:
                            img_path = os.path.join(temp_dir, f"img_{id(item)}.jpg")
                            pil_img.convert("RGB").save(img_path, format="JPEG")

                            # Enhanced Prompt: Force extraction of internal text/diagram labels
                            prompt = (
                                "Analyze this academic image, chart, or diagram. "
                                "Provide a highly detailed explanation of its core concepts. "
                                "CRITICAL: If there is any text, formula, or table visible inside the image, transcribe it accurately."
                            )
                            future = executor.submit(
                                gemini_client.describe_image, img_path, prompt
                            )
                            document_flow.append({"type": "image", "future": future})
                    except Exception as e:
                        print(f"[_process_pdf_logic] Failed to queue image: {e}")

                elif hasattr(item, "export_to_markdown") and item.label == "table":
                    document_flow.append(
                        {
                            "type": "text",
                            "content": f"{page_marker}\n\n{item.export_to_markdown()}\n\n",
                        }
                    )
                else:
                    # Standard text, paragraphs, and headings
                    if hasattr(item, "export_to_markdown"):
                        document_flow.append(
                            {
                                "type": "text",
                                "content": f"{page_marker}{item.export_to_markdown()}",
                            }
                        )
                    elif hasattr(item, "text"):
                        document_flow.append(
                            {"type": "text", "content": f"{page_marker}{item.text}"}
                        )

            # 4. Resolve futures and assemble the final markdown. MOVED INSIDE
            # the ThreadPool/TempDir block to prevent FileNotFoundError race
            # conditions
            final_md_parts = []
            for flow_item in document_flow:
                if flow_item["type"] == "text":
                    final_md_parts.append(flow_item["content"])
                elif flow_item["type"] == "image":
                    try:
                        # This blocks until the specific thread finishes
                        caption = flow_item["future"].result()
                        final_md_parts.append(
                            f"\n\n> **[Extracted Image/Diagram]**: {caption}\n\n"
                        )
                    except Exception as e:
                        print(
                            f"[_process_pdf_logic] Gemini Vision failed for an image: {e}"
                        )

    return "\n".join(final_md_parts)


def _process_video_logic(file_path: str) -> str:
    print(
        f"[_process_video_logic] Extracting transcript and scenes from {file_path}..."
    )

    # 1. Transcribe Audio (Strictly enforce CUDA & fp16 for your GPU)
    print("Running faster-whisper on GPU...")
    # Use cached global model to prevent VRAM memory leaks
    model = IngestionService.get_whisper_model()
    segments, _ = model.transcribe(file_path, beam_size=5)

    transcript_data = [
        {"start": s.start, "end": s.end, "text": s.text} for s in segments
    ]

    # 2. Detect Scenes using PySceneDetect
    print("Running PySceneDetect...")
    scene_list = detect(file_path, ContentDetector(threshold=27.0))

    # 3. Extract middle frame for each scene and get Gemini description
    cap = cv2.VideoCapture(file_path)
    scenes_data = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            futures_data = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for i, scene in enumerate(scene_list):
                    start_frame = scene[0].get_frames()
                    end_frame = scene[1].get_frames()
                    mid_frame = start_frame + (end_frame - start_frame) // 2

                    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
                    ret, frame = cap.read()

                    if ret:
                        frame_path = os.path.join(temp_dir, f"scene_{i}.jpg")
                        cv2.imwrite(frame_path, frame)

                        print(
                            f"[_process_video_logic] Queuing scene {i + 1} for description..."
                        )
                        future = executor.submit(
                            gemini_client.describe_image,
                            frame_path,
                            "Describe the educational content of this presentation slide or video frame. Extract any bullet points, titles, or diagrams visible.",
                        )
                        futures_data.append(
                            {
                                "start_time": scene[0].get_seconds(),
                                "end_time": scene[1].get_seconds(),
                                "future": future,
                            }
                        )

                # Resolve all threads before the temp_dir is destroyed
                for data in futures_data:
                    try:
                        caption = data["future"].result()
                        scenes_data.append(
                            {
                                "start_time": data["start_time"],
                                "end_time": data["end_time"],
                                "caption": caption,
                            }
                        )
                    except Exception as e:
                        print(f"[_process_video_logic] Failed to describe scene: {e}")
    finally:
        # Guarantee memory release to prevent OpenCV memory leaks in Celery workers
        cap.release()

    # 4. Interleave scenes with their corresponding transcripts
    final_text = []

    # CRITICAL: Fallback for videos with no scene changes (static visual)
    if not scenes_data:
        final_text.append("\n## Video Content (No Scene Changes Detected)")
        full_transcript = " ".join([t["text"] for t in transcript_data])
        final_text.append(
            full_transcript if full_transcript else "*(No dialogue detected)*"
        )
        return "\n".join(final_text)

    for i, scene in enumerate(scenes_data):
        final_text.append(
            f"\n## Scene {i + 1} (Timestamp: {scene['start_time']:.2f}s - {scene['end_time']:.2f}s)"
        )
        final_text.append(f"> **[Visual Content]**: {scene['caption']}\n")

        # Match transcripts overlapping this scene
        scene_transcripts = [
            t["text"]
            for t in transcript_data
            if (
                (t["start"] >= scene["start_time"] and t["start"] < scene["end_time"])
                or (t["end"] > scene["start_time"] and t["end"] <= scene["end_time"])
                or (t["start"] <= scene["start_time"] and t["end"] >= scene["end_time"])
            )
        ]

        if scene_transcripts:
            final_text.append(" ".join(scene_transcripts).strip())
        else:
            final_text.append("*(No dialogue in this segment)*")

    return "\n".join(final_text)
