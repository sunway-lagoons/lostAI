"""Validate, store, replace, and delete reference/query images."""

from pathlib import Path
from typing import List, Optional, Set
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os

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


def store_image(file: FileStorage, tags: Optional[List[str]] = None) -> dict:
    if not validate_image(file):
        raise ValueError(
            f"Invalid file or unsupported format. Allowed: {sorted(list(ALLOWED_EXTENSIONS))}"
        )

    clean_name = secure_filename(file.filename or "")
    ext = clean_name.rsplit(".", 1)[-1].lower()
    filename = clean_name
    destination = IMAGES_DIR / filename

    # Save image
    file.save(str(destination))

    # Ensure tags is a non-empty list; fallback to default if empty
    tags_list = [str(t).strip() for t in (tags or []) if str(t).strip()]
    if not tags_list:
        tags_list = ["default_item", "reference"]

    # Write tags to file
    tag_file_path = IMAGES_DIR / f"{Path(clean_name).stem}.txt"
    with open(tag_file_path, "w", encoding="utf-8") as f:
        # Join with newlines and add trailing newline
        f.write("\n".join(tags_list) + "\n")
        f.flush()
        os.fsync(f.fileno())  # Force write to physical storage immediately

    return {
        "filename": filename,
        "filepath": str(destination),
        "relative_path": f"tags/{filename}",
        "extension": ext,
        "tags": tags_list,
        "tag_file": str(tag_file_path)
    }