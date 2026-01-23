"""
Image Processing Service

Handles image resizing and cropping for profile pictures.
"""

import io
from typing import Literal

from PIL import Image


class ImageService:
    """Service for image manipulation."""

    @staticmethod
    def resize_for_avatar(
        image_data: bytes,
        size: int = 256,
        crop_mode: Literal["top", "center", "face"] = "top",
        output_format: str = "JPEG",
    ) -> bytes:
        """
        Resize and crop an image for use as an avatar.

        For portrait photos, this crops to a square focusing on the top
        of the image where faces typically are.

        Args:
            image_data: Raw image bytes
            size: Output size in pixels (square)
            crop_mode: Where to focus the crop
                - "top": Focus on top of image (best for portraits)
                - "center": Center crop (best for already-square images)
                - "face": Attempt face detection (not implemented)
            output_format: Output image format (JPEG, PNG, WEBP)

        Returns:
            Processed image bytes
        """
        # Open image
        img = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary (for JPEG output)
        if img.mode in ("RGBA", "P") and output_format.upper() == "JPEG":
            img = img.convert("RGB")

        # Get current dimensions
        width, height = img.size

        # Calculate crop box for square
        if width == height:
            # Already square, just resize
            crop_box = None
        elif width > height:
            # Landscape: crop sides, keep center
            left = (width - height) // 2
            crop_box = (left, 0, left + height, height)
        else:
            # Portrait: crop based on mode
            if crop_mode == "top":
                # Keep top portion (where face usually is)
                crop_box = (0, 0, width, width)
            elif crop_mode == "center":
                # Center crop
                top = (height - width) // 2
                crop_box = (0, top, width, top + width)
            else:
                # Default to top
                crop_box = (0, 0, width, width)

        # Crop if needed
        if crop_box:
            img = img.crop(crop_box)

        # Resize to target size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        img.save(output, format=output_format.upper(), quality=85, optimize=True)
        output.seek(0)

        return output.getvalue()

    @staticmethod
    def get_image_dimensions(image_data: bytes) -> tuple[int, int]:
        """
        Get dimensions of an image.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (width, height)
        """
        img = Image.open(io.BytesIO(image_data))
        return img.size

    @staticmethod
    def is_portrait(image_data: bytes) -> bool:
        """
        Check if an image is portrait orientation.

        Args:
            image_data: Raw image bytes

        Returns:
            True if height > width
        """
        width, height = ImageService.get_image_dimensions(image_data)
        return height > width
