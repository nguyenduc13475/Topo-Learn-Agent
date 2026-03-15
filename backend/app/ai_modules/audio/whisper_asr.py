from typing import List, Dict, Any
from faster_whisper import WhisperModel
import torch


class WhisperASR:
    def __init__(self, model_size: str = "large-v3"):
        """
        Load faster-whisper model. Automatically use CUDA (GPU) if available, else fallback to CPU.
        Upgraded to large-v3 for production-level transcription accuracy.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"

        print(
            f"[Production Setup] Loading faster-whisper model ({model_size}) on {self.device} with {self.compute_type}..."
        )
        self.model = WhisperModel(
            model_size, device=self.device, compute_type=self.compute_type
        )

    def transcribe_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio track from video with exact timestamps.
        """
        print(f"Transcribing audio from: {audio_path}")
        # beam_size=5 is standard for high quality
        segments, info = self.model.transcribe(audio_path, beam_size=5)

        print(
            f"Detected language '{info.language}' with probability {info.language_probability}"
        )

        transcript = []
        for segment in segments:
            transcript.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                }
            )

        print(f"Transcription complete. Extracted {len(transcript)} segments.")
        return transcript
