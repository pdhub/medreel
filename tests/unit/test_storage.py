import io

import pytest

from services.storage.backend import LocalStorage, R2Storage, get_json, put_json


def test_local_roundtrip(tmp_path):
    s = LocalStorage(tmp_path)
    assert not s.exists("job/a.bin")
    s.put("job/a.bin", io.BytesIO(b"hello"))
    assert s.exists("job/a.bin") and s.get("job/a.bin").read_bytes() == b"hello"
    assert s.url("job/a.bin").startswith("file://")
    put_json(s, "job/x.json", {"a": 1})
    assert get_json(s, "job/x.json") == {"a": 1}


def test_local_rejects_escaping_keys(tmp_path):
    with pytest.raises(ValueError):
        LocalStorage(tmp_path / "root").put("../outside", io.BytesIO(b""))


def test_missing_key(tmp_path):
    with pytest.raises(FileNotFoundError):
        LocalStorage(tmp_path).get("nope")


def test_r2_is_a_stub():
    with pytest.raises(NotImplementedError):
        R2Storage("bucket", "https://example.invalid").exists("k")
