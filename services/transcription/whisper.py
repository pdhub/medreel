from pathlib import Path
from typing import Protocol


class Transcriber(Protocol):
    def transcribe(self, path: Path) -> dict:
        """Return {"language": str, "words": [{"text", "start", "end", "probability"}]}."""


class FasterWhisperTranscriber:
    def __init__(self, model_size: str, compute_type: str):
        self.model_size, self.compute_type = model_size, compute_type
        self._model = None

    def transcribe(self, path):
        if self._model is None:  # load once per worker; the first job downloads the model into HF_HOME
            from faster_whisper import WhisperModel
            self._model = WhisperModel(self.model_size, device="cpu", compute_type=self.compute_type)
        segments, info = self._model.transcribe(str(path), word_timestamps=True)
        words = [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                  "probability": round(w.probability, 3)} for s in segments for w in (s.words or [])]
        return {"language": info.language, "words": words}
