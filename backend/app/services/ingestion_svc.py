import os
from typing import List
from pdf2image import convert_from_path
import pytesseract
from app.ai_modules.audio.scene_split import VideoSceneSplitter
from app.ai_modules.audio.whisper_asr import WhisperASR
from app.ai_modules.vision.yolo_layout import YoloLayoutAnalyzer
from app.ai_modules.vision.table_tf import TableTransformerModule
from app.ai_modules.llm.gemini_client import gemini_client


class IngestionService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split a large text string into smaller chunks by tokens or words.
        """
        words = text.split()
        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    @staticmethod
    def process_pdf_document(file_path: str) -> str:
        """
        Pipeline to process PDF: PDF to Image -> YOLO layout -> OCR/Table TF/Gemini Vision.
        Returns a single concatenated string.
        """
        print(f"Starting PDF processing pipeline for: {file_path}")

        yolo_analyzer = YoloLayoutAnalyzer()
        table_transformer = TableTransformerModule()

        final_document_text = []

        try:
            # 1. Convert PDF to list of images (one per page)
            print("Converting PDF pages to images...")
            pages = convert_from_path(file_path, 200)  # 200 DPI
            os.makedirs("data/uploads/temp", exist_ok=True)

            for page_num, page_image in enumerate(pages):
                page_img_path = f"data/uploads/temp/page_{page_num}.jpg"
                page_image.save(page_img_path, "JPEG")

                # 2. Analyze Layout with YOLO
                elements = yolo_analyzer.analyze_pdf_page(page_img_path)
                print(f"Found {len(elements)} elements on page {page_num + 1}.")

                for idx, element in enumerate(elements):
                    label = element["label"]
                    bbox = element["bbox"]

                    # Crop the element from the page image
                    cropped_img = page_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                    crop_path = f"data/uploads/temp/crop_{page_num}_{idx}.jpg"
                    cropped_img.save(crop_path, "JPEG")

                    # 3. Process based on Label
                    if label in ["Text", "Title"]:
                        # Extract real text using Tesseract OCR
                        print(f"Extracting text via OCR for element {idx}...")
                        extracted_text = pytesseract.image_to_string(
                            cropped_img
                        ).strip()
                        if extracted_text:
                            final_document_text.append(f"[{label}]: {extracted_text}")

                    elif label == "Table":
                        print(f"Extracting table structure for element {idx}...")
                        table_md = table_transformer.extract_table_to_markdown(
                            crop_path
                        )
                        final_document_text.append(f"[Table]:\n{table_md}")

                    elif label == "Figure":
                        print(f"Extracting figure description for element {idx}...")
                        figure_desc = gemini_client.describe_image(
                            image_path=crop_path,
                            prompt="Describe this academic figure in detail.",
                        )
                        final_document_text.append(
                            f"[Figure Description]: {figure_desc}"
                        )

            print("PDF processing completed successfully.")
            return "\n\n".join(final_document_text)

        except Exception as e:
            print(f"Error during PDF processing: {e}")
            return "Failed to process PDF content."

    @staticmethod
    def process_video_document(file_path: str) -> str:
        """
        Pipeline: PySceneDetect -> Whisper -> Gemini for keyframes -> Concat.
        """
        print(f"Starting Video processing pipeline for: {file_path}")

        # 1. Split scenes and get keyframes
        splitter = VideoSceneSplitter()
        scenes = splitter.split_scenes(file_path)

        # 2. Extract audio from video
        audio_path = file_path
        asr = WhisperASR()
        transcript = asr.transcribe_audio(audio_path)

        # 3. Loop through scenes, send keyframe to Gemini Vision API to get description
        print("Extracting insights from video keyframes...")
        scene_descriptions = {}
        for scene in scenes:
            frame_path = scene.get("keyframe_path")
            if os.path.exists(frame_path):
                desc = gemini_client.describe_image(
                    image_path=frame_path,
                    prompt="Describe the content of this presentation slide or video frame accurately.",
                )
                scene_descriptions[scene["scene_id"]] = desc
            else:
                scene_descriptions[scene["scene_id"]] = "No keyframe extracted."

        # 4. Construct the final document string mapping timestamps to text and descriptions
        final_document = []
        for t in transcript:
            line = f"[{t['start']} - {t['end']}] Transcript: {t['text']}"
            final_document.append(line)

        print("Video processing completed successfully.")
        return "\n".join(final_document)
