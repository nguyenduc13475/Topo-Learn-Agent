import os
from typing import List
from app.ai_modules.audio.scene_split import VideoSceneSplitter
from app.ai_modules.audio.whisper_asr import WhisperASR


class IngestionService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split a large text string into smaller chunks by tokens or words.
        (Simple word-based splitting for demonstration)
        """
        words = text.split()
        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    @staticmethod
    def process_pdf_document(file_path: str) -> str:
        """
        Pipeline to process PDF: YOLO layout -> Table TF -> Gemini Vision for Figures.
        Returns a single concatenated string.
        """
        print(f"Starting PDF processing pipeline for: {file_path}")
        # TODO: Implement YOLOv8 logic here
        # TODO: Implement Table Transformer logic here
        # TODO: Send cropped images to Gemini

        mock_concatenated_text = (
            "This is a mock text generated from the PDF processing pipeline."
        )
        return mock_concatenated_text

    @staticmethod
    def process_video_document(file_path: str) -> str:
        """
        Pipeline: PySceneDetect -> Whisper -> Gemini for keyframes -> Concat.
        """
        print(f"Starting Video processing pipeline for: {file_path}")

        # 1. Split scenes and get keyframes
        splitter = VideoSceneSplitter()
        scenes = splitter.split_scenes(file_path)

        # 2. Extract audio from video (You might need ffmpeg/moviepy here to rip audio first)
        # Assuming audio_path is ready for this example
        audio_path = file_path  # faster-whisper can often read directly from mp4
        asr = WhisperASR()
        transcript = asr.transcribe_audio(audio_path)

        # 3. Loop through scenes, send keyframe to Gemini Vision API to get description
        print("Extracting insights from video keyframes...")
        scene_descriptions = {}
        for scene in scenes:
            frame_path = scene.get("keyframe_path")
            # Make sure the file exists before calling API
            if os.path.exists(frame_path):
                from app.ai_modules.llm.gemini_client import gemini_client

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

        return "\n".join(final_document)
