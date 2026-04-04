"""Paths and loaders for bundled UI assets."""

from __future__ import annotations

from importlib.resources import files


def logo_png_bytes() -> bytes:
    return files("deepmeerkat.ui.assets").joinpath("DeepMeerkatLogo.png").read_bytes()
