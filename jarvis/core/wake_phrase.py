import json
import os
import queue
import threading

from vosk import Model, KaldiRecognizer


class WakePhraseDetector:
    """Listens for the wake phrase using Vosk offline speech recognition."""

    WAKE_PHRASE = "acorda criança vamos trabalhar"
    PARTIAL_MATCHES = ["acorda", "criança", "vamos", "trabalhar"]

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.environ.get(
                "VOSK_MODEL_PATH",
                os.path.expanduser("~/.jarvis/vosk-model-pt")
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Vosk model not found at {model_path}. "
                "Download a Portuguese model from https://alphacephei.com/vosk/models "
                "and extract it there, or set VOSK_MODEL_PATH."
            )
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        self._detected = threading.Event()
        self._running = False
        self._thread = None

    def reset(self):
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self._detected.clear()
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def feed(self, audio_chunk: bytes) -> bool:
        if self.recognizer.AcceptWaveform(audio_chunk):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").lower().strip()
            if self._matches_wake_phrase(text):
                return True
        else:
            partial = json.loads(self.recognizer.PartialResult())
            text = partial.get("partial", "").lower().strip()
            if self._matches_wake_phrase(text):
                return True
        return False

    def _matches_wake_phrase(self, text: str) -> bool:
        if not text:
            return False
        normalized = text.replace(",", "").replace(".", "").strip()
        if self.WAKE_PHRASE in normalized:
            return True
        matched = sum(1 for word in self.PARTIAL_MATCHES if word in normalized)
        return matched >= 3
