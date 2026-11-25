import json
import logging
import sys

# Only these extras are emitted, so transcript text or file contents never reach the logs by accident.
FIELDS = ("job_id", "node", "status", "duration_s", "method", "path", "status_code", "planner")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        out = {"ts": self.formatTime(record), "level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        out.update({k: getattr(record, k) for k in FIELDS if hasattr(record, k)})
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out)


def setup_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
    for noisy in ("httpx", "httpx2", "huggingface_hub"):  # model-download chatter
        logging.getLogger(noisy).setLevel(logging.WARNING)
