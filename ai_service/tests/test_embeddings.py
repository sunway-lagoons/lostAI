"""Embedding-quality tests that exercise the real encoder.

These require the model weights (downloaded via transformers) and torch. If
the model can't be loaded in the current environment, the whole module is
skipped so unrelated CI stays green.
"""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from ai_service.model import encoder

pytest.importorskip("torch")
pytest.importorskip("transformers")


@pytest.fixture(scope="module")
def loaded_encoder():
    try:
        encoder.load()
    except Exception as exc:  # network/model unavailable
        pytest.skip(f"encoder unavailable: {exc}")
    return encoder


def _solid(color, size=(96, 96)) -> Image.Image:
    return Image.new("RGB", size, color)


def test_output_shape_and_order(loaded_encoder):
    imgs = [_solid((255, 0, 0)), _solid((0, 128, 255)), _solid((0, 200, 0))]
    vecs = loaded_encoder.encode(imgs)
    assert vecs.shape[0] == 3
    assert vecs.dtype == np.float32
    if loaded_encoder.dim:
        assert vecs.shape[1] == loaded_encoder.dim


def test_vectors_are_unit_norm_and_finite(loaded_encoder):
    vecs = loaded_encoder.encode([_solid((10, 20, 30)), _solid((200, 100, 50))])
    assert np.all(np.isfinite(vecs))
    norms = np.linalg.norm(vecs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-4)


def test_identical_images_yield_near_identical_vectors(loaded_encoder):
    img = _solid((123, 222, 64))
    vecs = loaded_encoder.encode([img, img.copy()])
    # Cosine similarity of two identical inputs should be ~1.
    cos = float(np.dot(vecs[0], vecs[1]))
    assert cos > 0.999


def test_batch_matches_single(loaded_encoder):
    a = _solid((255, 0, 0))
    b = _solid((0, 0, 255))
    batch = loaded_encoder.encode([a, b])
    single_a = loaded_encoder.encode([a])[0]
    assert np.allclose(batch[0], single_a, atol=1e-4)
