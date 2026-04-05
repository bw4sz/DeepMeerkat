"""Fish weights cache and download helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

import deepmeerkat.fish_weights as fw


def test_ensure_explicit_path(tmp_path: Path) -> None:
    w = tmp_path / "custom.pth"
    w.write_bytes(b"x")
    assert fw.ensure_fish_weights(str(w)) == w.resolve()


def test_ensure_explicit_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Leave weights empty"):
        fw.ensure_fish_weights(str(tmp_path / "missing.pth"))


def test_auto_download_verifies_and_caches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = b"fake-weights-payload"
    good = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(fw, "FISH_WEIGHTS_SHA256_HEX", good)
    monkeypatch.setattr(fw, "FISH_WEIGHTS_SIZE_BYTES", len(payload))
    cache = tmp_path / "model.pth"
    monkeypatch.setattr(fw, "fish_weights_cache_path", lambda: cache)

    class _Resp:
        def __init__(self, data: bytes) -> None:
            self._buf = data
            self.headers = {"Content-Length": str(len(data))}

        def read(self, n: int = -1) -> bytes:
            if not self._buf:
                return b""
            if n is None or n < 0:
                out = self._buf
                self._buf = b""
                return out
            out, self._buf = self._buf[:n], self._buf[n:]
            return out

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> None:
            pass

    with patch.object(fw, "urlopen", return_value=_Resp(payload)):
        out = fw.ensure_fish_weights("")
    assert out == cache
    assert cache.read_bytes() == payload


def test_cached_skips_download(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = b"cached"
    good = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(fw, "FISH_WEIGHTS_SHA256_HEX", good)
    cache = tmp_path / "model.pth"
    cache.write_bytes(payload)
    monkeypatch.setattr(fw, "fish_weights_cache_path", lambda: cache)

    with patch.object(fw, "urlopen") as m_url:
        assert fw.ensure_fish_weights("") == cache
    m_url.assert_not_called()
