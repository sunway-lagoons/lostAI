"""AI inference service (Flask).

Routes:
  POST /embed   Accept one or more image files; return an ordered embedding per image.
  POST /rank    Given query embeddings + candidate objects, return ranked
                match confidence and per-tag confidence. Stateless: candidate
                reference embeddings are supplied by the caller.
  GET  /health  Report service readiness and model version.

The service stores nothing (no DB, no image files, no stored embeddings). The
app backend owns persistence and supplies candidates on each /rank call.
"""

from __future__ import annotations

import math

from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

from ai_service.config import config
from ai_service.model import encoder
from ai_service.preprocess import ImageDecodeError, decode_image
from ai_service.ranking import RankInputError, parse_request, rank


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "model_version": config.model_version,
                "model_loaded": encoder.is_loaded,
            }
        )

    @app.post("/embed")
    def embed():
        field = config.images_field
        files = [f for f in request.files.getlist(field) if f and f.filename]

        # --- validate request shape ---
        if not files:
            return _error(
                f"no images provided; send 1-{config.max_images} files in the "
                f"'{field}' field",
                400,
            )
        if len(files) < config.min_images:
            return _error(
                f"too few images: got {len(files)}, minimum {config.min_images}",
                400,
            )
        if len(files) > config.max_images:
            return _error(
                f"too many images: got {len(files)}, maximum {config.max_images}",
                400,
            )

        # --- decode and validate each image (order preserved) ---
        images = []
        for index, storage in enumerate(files):
            raw = storage.read()
            if len(raw) > config.max_file_bytes:
                return _error(
                    f"image at index {index} exceeds per-file limit of "
                    f"{config.max_file_bytes} bytes",
                    413,
                )
            try:
                images.append(decode_image(raw))
            except ImageDecodeError as exc:
                return _error(f"image at index {index}: {exc}", 400)

        # --- embed ---
        try:
            vectors = encoder.encode(images)
        except Exception as exc:  # pragma: no cover - infra/runtime failure
            app.logger.exception("embedding failed")
            return _error(f"inference failed: {exc}", 500)

        embeddings = [
            {"input_index": i, "vector": vectors[i].tolist()}
            for i in range(len(images))
        ]
        return jsonify(
            {"model_version": config.model_version, "embeddings": embeddings}
        )

    @app.post("/rank")
    def rank_route():
        payload = request.get_json(silent=True)
        if payload is None:
            return _error("request body must be valid JSON", 400)

        try:
            queries, candidates, threshold, top_k = parse_request(payload)
        except RankInputError as exc:
            return _error(str(exc), 400)

        # Substitute configured defaults when the caller omits them.
        if math.isnan(threshold):
            threshold = config.match_threshold
        if top_k <= 0:
            top_k = config.rank_top_k

        result = rank(queries, candidates, threshold, top_k)
        result["model_version"] = config.model_version
        result["threshold"] = threshold
        return jsonify(result)

    @app.errorhandler(RequestEntityTooLarge)
    def _too_large(_exc):
        return _error(
            f"request body exceeds limit of {config.max_content_length} bytes",
            413,
        )

    return app


# Module-level app for `flask run` / WSGI servers.
app = create_app()


if __name__ == "__main__":
    # Local dev only. In production run behind a WSGI server and keep this
    # service private to the app backend (not exposed to the public internet).
    app.run(host="127.0.0.1", port=8001)
