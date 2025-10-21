import cv2

PREFIX = "debug/"

def dump_image(file_name: str, image: cv2.Mat) -> None:
    """Utility function to dump an image to a file for debugging."""
    cv2.imwrite(f"{PREFIX}{file_name}", image)
