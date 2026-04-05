"""Download and cache Community Fish Detector weights (RF-DETR Nano)."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from threading import Event
from urllib.error import URLError
from urllib.request import Request, urlopen

from platformdirs import user_cache_dir

# Pinned to upstream release cfd-2026.02.02-rf-detr-nano (digest from GitHub API).
FISH_WEIGHTS_FILENAME = "community-fish-detector-2026.02.02-rf-detr-nano-640.pth"
FISH_WEIGHTS_URL = (
    "https://github.com/filippovarini/community-fish-detector/releases/download/"
    f"cfd-2026.02.02-rf-detr-nano/{FISH_WEIGHTS_FILENAME}"
)
FISH_WEIGHTS_SHA256_HEX = "076b0a80d5dbc3361fb2be707d521ce96fe990b453fb1c215d99194fc65b4762"
FISH_WEIGHTS_SIZE_BYTES = 122_064_141

_READ_CHUNK = 1024 * 1024  # 1 MiB


def fish_weights_cache_dir() -> Path:
    """Directory where the default fish `.pth` is stored after first download."""
    return Path(user_cache_dir("deepmeerkat", appauthor=False)) / "fish"


def fish_weights_cache_path() -> Path:
    """Full path to the cached default fish weights file."""
    return fish_weights_cache_dir() / FISH_WEIGHTS_FILENAME


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(_READ_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _download_to_path(
    url: str,
    dest: Path,
    *,
    expected_size: int,
    progress: Callable[[float, str], None] | None,
    cancel: Event | None,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".download")
    req = Request(
        url,
        headers={"User-Agent": "DeepMeerkat/3.1 (+https://github.com/bw4sz/DeepMeerkat)"},
    )
    try:
        with urlopen(req, timeout=300) as resp:
            total = int(resp.headers.get("Content-Length") or 0) or expected_size
            got = 0
            with tmp.open("wb") as out:
                while True:
                    if cancel and cancel.is_set():
                        raise RuntimeError("Cancelled while downloading fish weights.")
                    chunk = resp.read(_READ_CHUNK)
                    if not chunk:
                        break
                    out.write(chunk)
                    got += len(chunk)
                    if progress and total > 0:
                        frac = min(1.0, got / float(total))
                        mb_got = got // (1024 * 1024)
                        mb_tot = max(1, total // (1024 * 1024))
                        progress(
                            frac,
                            f"Downloading fish model… ({mb_got} / ~{mb_tot} MiB)",
                        )
        tmp.replace(dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def ensure_fish_weights(
    weights_path: str,
    *,
    progress: Callable[[float, str], None] | None = None,
    cancel: Event | None = None,
) -> Path:
    """
    Resolve `.pth` weights: use an explicit path if set and valid; otherwise use the
    cache path, downloading and verifying on first use.
    """
    raw = (weights_path or "").strip()
    if raw:
        p = Path(raw).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(
                f"Fish model weights not found: {p}\n"
                "Leave weights empty to download automatically, or set a valid .pth path."
            )
        if progress:
            progress(1.0, "Using fish weights from disk…")
        return p

    cache = fish_weights_cache_path()
    if cache.is_file():
        if progress:
            progress(0.0, "Verifying cached fish model…")
        digest = _sha256_file(cache)
        if digest == FISH_WEIGHTS_SHA256_HEX:
            if progress:
                progress(1.0, "Using cached fish model…")
            return cache
        cache.unlink(missing_ok=True)

    if progress:
        progress(0.0, "Downloading Community Fish Detector weights (~116 MB, one-time)…")

    try:
        _download_to_path(
            FISH_WEIGHTS_URL,
            cache,
            expected_size=FISH_WEIGHTS_SIZE_BYTES,
            progress=progress,
            cancel=cancel,
        )
    except URLError as e:
        raise RuntimeError(
            "Could not download fish detector weights. Check your network, or download manually "
            "from:\n"
            f"  {FISH_WEIGHTS_URL}\n"
            "Then set --fish-weights or the GUI Weights field to that file."
        ) from e

    if progress:
        progress(0.95, "Verifying download…")
    digest = _sha256_file(cache)
    if digest != FISH_WEIGHTS_SHA256_HEX:
        cache.unlink(missing_ok=True)
        raise RuntimeError(
            "Downloaded fish weights failed checksum verification. Delete the cache folder and "
            f"try again, or install manually. Cache: {cache.parent}"
        )

    if progress:
        progress(1.0, "Fish model ready.")
    return cache
