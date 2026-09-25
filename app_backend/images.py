"""Validate, store, replace, and delete reference/query images."""

# TODO: validate_image(), store_image(), replace_image(), delete_image()

from pathlib import Path
from typing import Optional, Set
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# Resolve the root 'lostAI/images' directory relative to this file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "images"

ALLOWED_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "webp"}

# Ensure the destination images folder exists
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def validate_image(file: Optional[FileStorage]) -> bool:
    """Validate that the file exists, has a filename, and has an allowed extension."""
    if not file or not file.filename:
        return False
    
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    return ext in ALLOWED_EXTENSIONS


def store_image(file: FileStorage) -> dict:
    """Validate and store an incoming uploaded image directly into the images/ folder.

    Args:
        file: The Werkzeug FileStorage object from request.files.
        prefix: Prefix for the stored file ('ref', 'query', etc.).

    Returns:
        dict: Metadata with filename, absolute path, relative path, and extension.

    Raises:
        ValueError: If the file is missing or has an unsupported extension.
    """
    if not validate_image(file):
        raise ValueError(
            f"Invalid file or unsupported format. Allowed: {sorted(list(ALLOWED_EXTENSIONS))}"
        )

    # Sanitize the uploaded name so it cannot escape the images directory.
    clean_name = secure_filename(file.filename or "")
    ext = clean_name.rsplit(".", 1)[-1].lower()
    filename = clean_name
    destination = IMAGES_DIR / filename

    # Save to lostAI/images/
    file.save(str(destination))

    return {
        "filename": filename,
        "filepath": str(destination),
        "relative_path": f"images/{filename}",
        "extension": ext
    }