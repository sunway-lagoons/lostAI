"""Image decoding and normalization.

Reference and query images go through the exact same pipeline: decode with
Pillow, apply EXIF orientation, and convert to RGB. The model's own image
processor (in ``model.py``) handles resizing and tensor normalization.
"""

from __future__ import annotations

import io

from PIL import Image, ImageOps, UnidentifiedImageError


class ImageDecodeError(ValueError):
    """Raised when an upload is empty, corrupt, or an unsupported format."""


def decode_image(raw: bytes) -> Image.Image:
    """Decode raw bytes into an RGB :class:`PIL.Image.Image`.

    Applies EXIF orientation so photos taken in different orientations are
    normalized before embedding.

    Raises:
        ImageDecodeError: if the bytes are empty, not a valid image, or use an
            unsupported/undecodable format.
    """
    if not raw:
        raise ImageDecodeError("empty image payload")

    try:
        with Image.open(io.BytesIO(raw)) as img:
            # Respect the camera's EXIF orientation tag, then drop to RGB.
            img = ImageOps.exif_transpose(img)
            rgb = img.convert("RGB")
            # Force a full load while the buffer is open, then detach from it.
            rgb.load()
            return rgb
    except ImageDecodeError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageDecodeError(f"could not decode image: {exc}") from exc
