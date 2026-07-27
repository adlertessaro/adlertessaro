import json
import os

from vosk import Model, KaldiRecognizer


class SpeechRecognizer:
    """Converts speech audio to text using Vosk."""

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.environ.get(
                "VOSK_MODEL_PATH",
                os.path.expanduser("~/.jarvis/vosk-model-pt")
            )
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def feed(self, audio_chunk: bytes) -> str | None:
        if self.recognizer.AcceptWaveform(audio_chunk):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text
        return None

    def finalize(self) -> str | None:
        result = json.loads(self.recognizer.FinalResult())
        text = result.get("text", "").strip()
        return text if text else None
