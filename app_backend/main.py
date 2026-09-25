"""App backend HTTP routes (FastAPI).

Routes:
  POST   /objects       Register object, views, and tags; store embeddings.
  POST   /match         Accept query image(s); return ranked object matches.
  GET    /search?q=...  Fuzzy name/tag search.
  DELETE /objects/{id}  Delete object metadata, images, and embeddings.
"""

# TODO: define FastAPI app and wire routes to images/search/matching modules

import os
from flask import Flask, jsonify, request

# Import helpers from your sibling modules if needed
# from .search import execute_search
# from .matching import rank_matches

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

    # Here you would call your store_image function from images.py
    try:
        from .images import store_image
        result = store_image(file)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)