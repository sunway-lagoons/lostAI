import io
import json
from datetime import datetime
from pathlib import Path

from app_backend import images
from app_backend.main import app


def test_upload_image_persists_item_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(images, "IMAGES_DIR", tmp_path)
    client = app.test_client()

    response = client.post(
        "/api/upload-image",
        data={
            "file": (io.BytesIO(b"image bytes"), "wallet.jpg"),
            "location_pin": "37.7749,-122.4194",
            "timestamp": "2026-09-25T12:30:00Z",
            "scan_surfaces": '["front", "back", "inside"]',
            "description": "Brown leather bifold wallet",
            "email": "finder@example.com",
            "name": "Alex Finder",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    body = response.get_json()
    expected_metadata = {
        "location_pin": "37.7749,-122.4194",
        "timestamp": "2026-09-25T12:30:00Z",
        "scan_surfaces": ["front", "back", "inside"],
        "description": "Brown leather bifold wallet",
        "email": "finder@example.com",
        "name": "Alex Finder",
    }
    assert body["metadata"] == expected_metadata

    metadata_path = Path(body["metadata_file"])
    assert metadata_path == tmp_path / "wallet.metadata.txt"
    assert json.loads(metadata_path.read_text(encoding="utf-8")) == expected_metadata
    assert (tmp_path / "wallet.txt").read_text(encoding="utf-8") == (
        "wallet\nleather\naccessory\n"
    )


def test_upload_image_defaults_timestamp_to_utc(monkeypatch, tmp_path):
    monkeypatch.setattr(images, "IMAGES_DIR", tmp_path)
    client = app.test_client()

    response = client.post(
        "/api/upload-image",
        data={"file": (io.BytesIO(b"image bytes"), "wallet.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    timestamp = response.get_json()["metadata"]["timestamp"]
    parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert parsed_timestamp.utcoffset().total_seconds() == 0