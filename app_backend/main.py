"""App backend HTTP routes (Flask).

Routes:
  POST   /objects       Register object, views, and tags; store embeddings.
  POST   /match         Accept query image(s); return ranked object matches.
  GET    /search?q=...  Fuzzy name/tag search.
  DELETE /objects/{id}  Delete object metadata, images, and embeddings.
"""

import json
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    raw_tags = request.form.get("tags")
    parsed_tags = []

    if raw_tags:
        raw_tags = raw_tags.strip()
        # Handle JSON array format: ["tag1", "tag2"]
        if raw_tags.startswith("[") and raw_tags.endswith("]"):
            try:
                loaded = json.loads(raw_tags)
                if isinstance(loaded, list):
                    parsed_tags = [str(t).strip() for t in loaded]
            except json.JSONDecodeError:
                return jsonify({"error": "Malformed JSON in tags"}), 400
        else:
            # Handle comma-separated format: tag1, tag2, tag3
            parsed_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

    # If still empty, use hardcoded default tags
    if not parsed_tags:
        parsed_tags = ["wallet", "leather", "accessory"]

    raw_surfaces = request.form.get("scan_surfaces", "").strip()
    scan_surfaces = []
    if raw_surfaces:
        if raw_surfaces.startswith("["):
            try:
                loaded_surfaces = json.loads(raw_surfaces)
            except json.JSONDecodeError:
                return jsonify({"error": "Malformed JSON in scan_surfaces"}), 400
            if not isinstance(loaded_surfaces, list) or not all(
                isinstance(surface, str) for surface in loaded_surfaces
            ):
                return jsonify({"error": "scan_surfaces must be a list of strings"}), 400
            scan_surfaces = [
                surface.strip() for surface in loaded_surfaces if surface.strip()
            ]
        else:
            scan_surfaces = [
                surface.strip()
                for surface in raw_surfaces.split(",")
                if surface.strip()
            ]

    metadata = {
        "location_pin": request.form.get("location_pin", "").strip(),
        "timestamp": request.form.get("timestamp", "").strip()
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scan_surfaces": scan_surfaces,
        "description": request.form.get("description", "").strip(),
        "email": request.form.get("email", "").strip(),
        "name": request.form.get("name", "").strip(),
    }

    try:
        from .images import store_image
        result = store_image(file, tags=parsed_tags, metadata=metadata)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)