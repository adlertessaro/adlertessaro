import logging
import struct
import threading
import time

import numpy as np
import pyaudio

from .clap_detector import ClapDetector
from .wake_phrase import WakePhraseDetector

logger = logging.getLogger("jarvis.listener")

RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1


class State:
    IDLE = "idle"
    WAITING_PHRASE = "waiting_phrase"
    ACTIVE = "active"


class Listener:
    """
    Main audio listener pipeline.

    States:
      IDLE -> detects claps -> WAITING_PHRASE
      WAITING_PHRASE -> detects wake phrase -> ACTIVE
      WAITING_PHRASE -> timeout (5s) -> IDLE
      ACTIVE -> silence timeout -> IDLE
    """

    def __init__(self, on_state_change=None, on_speech=None, on_audio_level=None):
        self.state = State.IDLE
        self.on_state_change = on_state_change or (lambda s: None)
        self.on_speech = on_speech or (lambda t: None)
        self.on_audio_level = on_audio_level or (lambda l: None)

        self.clap_detector = ClapDetector()
        self.wake_detector = WakePhraseDetector()
        self.speech_recognizer = None

        self._running = False
        self._thread = None
        self._pa = None
        self._stream = None
        self._phrase_timeout = 8.0
        self._phrase_timer_start = 0
        self._silence_timeout = 2.0
        self._last_voice_time = 0

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Listener started — waiting for claps")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        self._cleanup_audio()

    def _run(self):
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        while self._running:
            try:
                raw = self._stream.read(CHUNK, exception_on_overflow=False)
                audio = np.frombuffer(raw, dtype=np.int16)
                level = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)) / 32768.0)
                self.on_audio_level(level)
                self._process(raw, audio, level)
            except Exception as e:
                logger.error(f"Listener error: {e}")
                time.sleep(0.1)
        self._cleanup_audio()

    def _process(self, raw: bytes, audio: np.ndarray, level: float):
        if self.state == State.IDLE:
            if self.clap_detector.feed(audio):
                logger.info("Claps detected! Listening for wake phrase...")
                self._set_state(State.WAITING_PHRASE)
                self.wake_detector.reset()
                self._phrase_timer_start = time.time()

        elif self.state == State.WAITING_PHRASE:
            if time.time() - self._phrase_timer_start > self._phrase_timeout:
                logger.info("Wake phrase timeout, back to idle")
                self._set_state(State.IDLE)
                return
            if self.wake_detector.feed(raw):
                logger.info("Wake phrase detected! Activating...")
                self._set_state(State.ACTIVE)
                self._last_voice_time = time.time()
                self._init_speech_recognizer()

        elif self.state == State.ACTIVE:
            if level > 0.01:
                self._last_voice_time = time.time()
            if self.speech_recognizer:
                text = self.speech_recognizer.feed(raw)
                if text:
                    self.on_speech(text)
                    self._last_voice_time = time.time()
            if time.time() - self._last_voice_time > self._silence_timeout:
                pass

    def _init_speech_recognizer(self):
        from .speech_recognizer import SpeechRecognizer
        self.speech_recognizer = SpeechRecognizer()

    def deactivate(self):
        self._set_state(State.IDLE)
        self.clap_detector.reset()
        self.speech_recognizer = None

    def _set_state(self, new_state):
        old = self.state
        self.state = new_state
        if old != new_state:
            logger.info(f"State: {old} -> {new_state}")
            self.on_state_change(new_state)

    def _cleanup_audio(self):
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
