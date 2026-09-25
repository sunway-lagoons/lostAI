"""API-level tests for the Flask service.

These focus on routing, validation, and error handling. The encoder is
replaced with a lightweight fake so the tests run without downloading the
model or needing a GPU.
"""

from __future__ import annotations

import dataclasses
import io

import numpy as np
import pytest
from PIL import Image

from ai_service import model as model_module
from ai_service.app import create_app
from ai_service.config import config

FAKE_DIM = 8


class FakeEncoder:
    """Deterministic stand-in for the real Encoder."""

    is_loaded = True
    dim = FAKE_DIM

    def load(self) -> None:  # noqa: D401 - no-op
        pass

    def encode(self, images):
        # Return a unit vector per image; contents don't matter for API tests.
        n = len(images)
        vecs = np.zeros((n, FAKE_DIM), dtype=np.float32)
        if n:
            vecs[:, 0] = 1.0
        return vecs


@pytest.fixture()
def client(monkeypatch):
    fake = FakeEncoder()
    # The app reads the encoder imported into its module namespace.
    monkeypatch.setattr("ai_service.app.encoder", fake)
    monkeypatch.setattr(model_module, "encoder", fake)
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _png_bytes(color=(255, 0, 0), size=(32, 32)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


def _files(n: int):
    return [
        (io.BytesIO(_png_bytes()), f"img_{i}.png") for i in range(n)
    ]


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["model_version"] == config.model_version


def test_embed_single_image(client):
    data = {config.images_field: _files(1)}
    resp = client.post("/embed", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["model_version"] == config.model_version
    assert len(body["embeddings"]) == 1
    assert body["embeddings"][0]["input_index"] == 0
    assert len(body["embeddings"][0]["vector"]) == FAKE_DIM


def test_embed_preserves_order(client):
    data = {config.images_field: _files(3)}
    resp = client.post("/embed", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    indices = [e["input_index"] for e in resp.get_json()["embeddings"]]
    assert indices == [0, 1, 2]


def test_embed_no_images_is_400(client):
    resp = client.post("/embed", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_embed_too_many_images_is_400(client):
    data = {config.images_field: _files(config.max_images + 1)}
    resp = client.post("/embed", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_embed_corrupt_image_is_400(client):
    data = {config.images_field: [(io.BytesIO(b"not an image"), "bad.png")]}
    resp = client.post("/embed", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "index 0" in resp.get_json()["error"]


def test_embed_oversized_file_is_413(client, monkeypatch):
    # Config is frozen, so swap in a copy with a tiny per-file limit.
    small = dataclasses.replace(config, max_file_bytes=10)
    monkeypatch.setattr("ai_service.app.config", small)
    data = {config.images_field: _files(1)}
    resp = client.post("/embed", data=data, content_type="multipart/form-data")
    assert resp.status_code == 413


# --- /rank (no model needed; pure vector math) ---


def _unit3(*c):
    v = np.asarray(c, dtype=np.float32)
    return (v / np.linalg.norm(v)).tolist()


def test_rank_returns_confidence_and_tag_confidence(client):
    q = _unit3(1, 0, 0)
    body = {
        "queries": [q],
        "candidates": [
            {"object_id": "a", "tags": ["wallet"], "views": [{"view_label": "top", "vector": q}]},
            {"object_id": "b", "tags": ["bottle"], "views": [{"view_label": "top", "vector": _unit3(0, 1, 0)}]},
        ],
    }
    resp = client.post("/rank", json=body)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["matches"][0]["object_id"] == "a"
    assert data["matches"][0]["confidence"] > 0.99
    assert data["decision"] == "match"
    assert {t["tag"] for t in data["tag_confidence"]} == {"wallet", "bottle"}
    assert data["model_version"] == config.model_version


def test_rank_uses_config_defaults_when_omitted(client):
    q = _unit3(1, 0, 0)
    body = {"queries": [q], "candidates": [{"object_id": "a", "views": [{"vector": q}]}]}
    resp = client.post("/rank", json=body)
    assert resp.status_code == 200
    # threshold echoed back should be the configured default.
    assert resp.get_json()["threshold"] == config.match_threshold


def test_rank_rejects_non_json(client):
    resp = client.post("/rank", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_rank_rejects_bad_payload(client):
    resp = client.post("/rank", json={"queries": [], "candidates": []})
    assert resp.status_code == 400
