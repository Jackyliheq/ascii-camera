import os
from collections.abc import Generator
import cv2
import numpy as np


def load_image(image_path: str) -> np.ndarray:
    """Load an image file from a path, verifying its existence and validity."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: '{image_path}'")

    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError(
            f"Unable to read file at '{image_path}'. Ensure it is a valid image."
        )

    return frame


def stream_webcam(
    camera_index: int = 0, mirror: bool = True
) -> Generator[np.ndarray, None, None]:
    """Capture live webcam frames and yield them continuously."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not access webcam at index {camera_index}. Check camera permissions."
        )

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                # Capture issues or stream closed, terminate gracefully
                break

            if mirror:
                frame = cv2.flip(frame, 1)

            yield frame
    finally:
        cap.release()