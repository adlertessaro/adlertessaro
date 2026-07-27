import io
import os
import platform
import subprocess
import tempfile
import threading


class Voice:
    """Text-to-speech output using macOS 'say' command or pyttsx3 fallback."""

    def __init__(self, on_speaking_start=None, on_speaking_end=None):
        self.on_speaking_start = on_speaking_start or (lambda: None)
        self.on_speaking_end = on_speaking_end or (lambda: None)
        self._lock = threading.Lock()
        self.is_mac = platform.system() == "Darwin"
        self.voice_name = os.environ.get("JARVIS_VOICE", "Luciana")
        self.rate = int(os.environ.get("JARVIS_VOICE_RATE", "180"))

    def speak(self, text: str):
        threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()

    def _speak_sync(self, text: str):
        with self._lock:
            self.on_speaking_start()
            try:
                if self.is_mac:
                    self._speak_mac(text)
                else:
                    self._speak_pyttsx3(text)
            finally:
                self.on_speaking_end()

    def _speak_mac(self, text: str):
        subprocess.run(
            ["say", "-v", self.voice_name, "-r", str(self.rate), text],
            check=True,
            capture_output=True,
        )

    def _speak_pyttsx3(self, text: str):
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        voices = engine.getProperty("voices")
        for v in voices:
            if "portuguese" in v.name.lower() or "brazil" in v.name.lower():
                engine.setProperty("voice", v.id)
                break
        engine.say(text)
        engine.runAndWait()
