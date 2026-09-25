"""Image encoder: one-time model load and batched embedding.

The processor and model are loaded exactly once (lazily, on first use) and
reused for every request. Embeddings are the model's global CLS token,
L2-normalized and returned as ``float32``.
"""

from __future__ import annotations

import threading
from typing import Sequence

import numpy as np
from PIL.Image import Image

from ai_service.config import config


class Encoder:
    """Wraps a pretrained vision transformer to produce image embeddings."""

    def __init__(self) -> None:
        self._processor = None
        self._model = None
        self._device = None
        self._dim: int | None = None
        self._lock = threading.Lock()

    # -- loading -----------------------------------------------------------

    def load(self) -> None:
        """Load the processor and model once. Safe to call repeatedly."""
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return

            import torch
            from transformers import AutoImageProcessor, AutoModel

            processor = AutoImageProcessor.from_pretrained(config.model_id)
            model = AutoModel.from_pretrained(config.model_id)
            model.eval()

            device = torch.device(config.device)
            try:
                model.to(device)
            except Exception:
                # Fall back to CPU if the requested device is unavailable.
                device = torch.device("cpu")
                model.to(device)

            self._processor = processor
            self._model = model
            self._device = device
            self._dim = int(getattr(model.config, "hidden_size", 0)) or None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def dim(self) -> int | None:
        return self._dim

    # -- inference ---------------------------------------------------------

    def encode(self, images: Sequence[Image]) -> np.ndarray:
        """Embed a batch of PIL images.

        Args:
            images: RGB images, already decoded and EXIF-normalized.

        Returns:
            ``(n, dim)`` ``float32`` array of L2-normalized CLS embeddings, in
            the same order as ``images``.
        """
        if not images:
            return np.empty((0, self._dim or 0), dtype=np.float32)

        self.load()
        import torch

        inputs = self._processor(images=list(images), return_tensors="pt")
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.inference_mode():
            outputs = self._model(**inputs)

        # Global CLS token: first position of the last hidden state.
        cls = outputs.last_hidden_state[:, 0, :]
        cls = torch.nn.functional.normalize(cls, p=2, dim=1)
        return cls.detach().cpu().numpy().astype(np.float32)


# Process-wide singleton encoder.
encoder = Encoder()
