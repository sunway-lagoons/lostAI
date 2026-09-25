"""Runtime configuration for the AI inference service.

All values can be overridden with environment variables so the service can be
tuned per deployment without code changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _resolve_device(requested: str | None) -> str:
    """Pick a torch device. Auto-detect when not explicitly requested."""
    if requested and requested.strip():
        return requested.strip()
    # Import lazily so config stays importable without torch installed.
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


@dataclass(frozen=True)
class Config:
    # Model / embedding identity.
    model_id: str = os.environ.get("AI_SERVICE_MODEL_ID", "facebook/dinov2-small")
    # Bumped whenever the model, preprocessing, or embedding method changes.
    # Stored embeddings must be regenerated on any change.
    model_version: str = os.environ.get(
        "AI_SERVICE_MODEL_VERSION", "facebook/dinov2-small:cls-l2-v1"
    )

    # Compute device: "cuda", "mps", "cpu", or "" to auto-detect.
    device: str = _resolve_device(os.environ.get("AI_SERVICE_DEVICE"))

    # Request validation limits.
    min_images: int = _env_int("AI_SERVICE_MIN_IMAGES", 1)
    max_images: int = _env_int("AI_SERVICE_MAX_IMAGES", 8)
    # Per-file size cap (bytes). Default 10 MiB.
    max_file_bytes: int = _env_int("AI_SERVICE_MAX_FILE_BYTES", 10 * 1024 * 1024)
    # Whole request-body cap (bytes) enforced by Flask. Default 64 MiB.
    max_content_length: int = _env_int(
        "AI_SERVICE_MAX_CONTENT_LENGTH", 64 * 1024 * 1024
    )

    # Multipart field name that carries the uploaded images (repeated).
    images_field: str = os.environ.get("AI_SERVICE_IMAGES_FIELD", "images")

    # Ranking defaults (used by /rank when the request omits them).
    # NOTE: this threshold is a placeholder. Calibrate it from held-out known
    # and unknown images; cosine similarity is not a calibrated probability.
    match_threshold: float = _env_float("AI_SERVICE_MATCH_THRESHOLD", 0.55)
    rank_top_k: int = _env_int("AI_SERVICE_RANK_TOP_K", 5)


# Singleton config instance imported across the service.
config = Config()
