from typing import List, Dict, Any
from faster_whisper import WhisperModel


class WhisperASR:
    def __init__(self, model_size: str = "small", device: str = "cpu"):
        """
        Load faster-whisper model. Use "cuda" if GPU is available.
        """
        print(f"Loading faster-whisper model ({model_size}) on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type="float32")

    def transcribe_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio track from video with timestamps.
        """
        print(f"Transcribing audio from: {audio_path}")
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

        return transcript
