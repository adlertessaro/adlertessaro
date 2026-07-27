#!/usr/bin/env python3
"""
Jarvis — Voice-activated personal assistant.

Activate with claps + "acorda criança, vamos trabalhar".
"""

import logging
import os
import signal
import sys
import time

from core.brain import Brain
from core.listener import Listener, State
from core.server import WebSocketServer
from core.voice import Voice

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("jarvis")


class Jarvis:
    def __init__(self):
        self.server = WebSocketServer()
        self.brain = Brain()
        self.voice = Voice(
            on_speaking_start=self._on_speaking_start,
            on_speaking_end=self._on_speaking_end,
        )
        self.listener = Listener(
            on_state_change=self._on_state_change,
            on_speech=self._on_speech,
            on_audio_level=self._on_audio_level,
        )
        self._speaking = False

    def start(self):
        logger.info("=" * 50)
        logger.info("  JARVIS — Assistente Pessoal")
        logger.info("  Ativação: palmas + 'acorda criança, vamos trabalhar'")
        logger.info("=" * 50)

        self.server.start()
        time.sleep(0.5)
        self.server.open_frontend()
        time.sleep(1)

        self.listener.start()
        self.server.broadcast("state", {"state": "idle"})

        try:
            signal.signal(signal.SIGINT, self._shutdown)
            signal.signal(signal.SIGTERM, self._shutdown)
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._shutdown()

    def _on_state_change(self, state):
        self.server.broadcast("state", {"state": state})
        if state == State.ACTIVE:
            logger.info("Jarvis activated!")
            greeting = self.brain.greet()
            logger.info(f"Jarvis: {greeting}")
            self.server.broadcast("response", {"text": greeting})
            self.voice.speak(greeting)

    def _on_speech(self, text):
        if self._speaking:
            return
        logger.info(f"User: {text}")
        self.server.broadcast("user_speech", {"text": text})

        response = self.brain.chat(text)
        logger.info(f"Jarvis: {response}")
        self.server.broadcast("response", {"text": response})
        self.voice.speak(response)

    def _on_audio_level(self, level):
        self.server.broadcast("audio_level", {"level": level})

    def _on_speaking_start(self):
        self._speaking = True
        self.server.broadcast("speaking", {"active": True})

    def _on_speaking_end(self):
        self._speaking = False
        self.server.broadcast("speaking", {"active": False})

    def _shutdown(self, *args):
        logger.info("Shutting down Jarvis...")
        self.listener.stop()
        sys.exit(0)


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.start()
