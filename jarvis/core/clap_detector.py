import numpy as np


class ClapDetector:
    """Detects clap patterns in audio frames."""

    def __init__(self, threshold=0.4, min_gap_ms=100, max_gap_ms=800, required_claps=2):
        self.threshold = threshold
        self.min_gap_samples = int(16000 * min_gap_ms / 1000)
        self.max_gap_samples = int(16000 * max_gap_ms / 1000)
        self.required_claps = required_claps
        self.clap_times = []
        self.sample_counter = 0
        self.in_clap = False
        self.silence_after_clap = 0

    def reset(self):
        self.clap_times = []
        self.sample_counter = 0
        self.in_clap = False
        self.silence_after_clap = 0

    def feed(self, audio_chunk: np.ndarray) -> bool:
        audio = audio_chunk.astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))

        is_loud = peak > self.threshold and rms > self.threshold * 0.3

        if is_loud and not self.in_clap:
            self.in_clap = True
            self.clap_times.append(self.sample_counter)
            self._prune_old_claps()
        elif not is_loud and self.in_clap:
            self.in_clap = False

        self.sample_counter += len(audio_chunk)

        if len(self.clap_times) >= self.required_claps:
            gaps_valid = True
            for i in range(1, len(self.clap_times)):
                gap = self.clap_times[i] - self.clap_times[i - 1]
                if gap < self.min_gap_samples or gap > self.max_gap_samples:
                    gaps_valid = False
                    break
            if gaps_valid:
                self.reset()
                return True

        return False

    def _prune_old_claps(self):
        if len(self.clap_times) < 2:
            return
        cutoff = self.sample_counter - self.max_gap_samples * (self.required_claps + 1)
        self.clap_times = [t for t in self.clap_times if t > cutoff]
