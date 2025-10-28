import cv2

PREFIX = "debug/"

def dump_image(file_name: str, image: cv2.Mat) -> None:
    """Utility function to dump an image to a file for debugging."""
    cv2.imwrite(f"{PREFIX}{file_name}", image)

def show_image(window_name: str, image: cv2.Mat) -> None:
    """Utility function to show an image in a window for debugging."""
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
