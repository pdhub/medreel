import io
import json
import shutil
from pathlib import Path
from typing import BinaryIO, Protocol


class StorageBackend(Protocol):
    def put(self, key: str, src: BinaryIO) -> None: ...
    def get(self, key: str) -> Path:
        """Return a local path to read the object from."""
    def url(self, key: str) -> str: ...
    def exists(self, key: str) -> bool: ...


class LocalStorage:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("storage key escapes the storage root")
        return path

    def put(self, key, src):
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_name(path.name + ".part")
        with open(part, "wb") as f:
            shutil.copyfileobj(src, f)
        part.replace(path)  # readers never see a half-written file

    def get(self, key):
        path = self._path(key)
        if not path.is_file():
            raise FileNotFoundError(key)
        return path

    def url(self, key):
        return self._path(key).as_uri()

    def exists(self, key):
        return self._path(key).is_file()


class R2Storage:
    """Cloudflare R2 backend: not implemented on Day 1.

    Planned signed-upload flow:
    1. POST /api/jobs/{id}/upload-url returns a presigned PUT URL for key "{id}/source.mp4" (short expiry,
       Content-Type video/mp4, size limit in the signature).
    2. The client PUTs the file straight to R2, so video bytes never pass through the API.
    3. POST /api/jobs/{id}/upload-complete makes the API HEAD the object, ffprobe it through a presigned GET
       and move the job to "uploaded", the same checks the multipart endpoint runs today.
    get() downloads to a local cache path for FFmpeg; url() returns a presigned GET.
    """

    def __init__(self, bucket: str, endpoint_url: str):
        self.bucket, self.endpoint_url = bucket, endpoint_url

    def put(self, key, src):
        raise NotImplementedError("R2Storage is a Day 1 stub")

    def get(self, key):
        raise NotImplementedError("R2Storage is a Day 1 stub")

    def url(self, key):
        raise NotImplementedError("R2Storage is a Day 1 stub")

    def exists(self, key):
        raise NotImplementedError("R2Storage is a Day 1 stub")


def put_json(storage: StorageBackend, key: str, obj) -> None:
    storage.put(key, io.BytesIO(json.dumps(obj).encode()))


def get_json(storage: StorageBackend, key: str):
    return json.loads(storage.get(key).read_text())
