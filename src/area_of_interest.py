import cv2
import pyautogui

from utils import dump_image


TEMP_FILE = "examples/screen_shot.png"

def is_valid_area(area: cv2.Mat) -> bool:
    area_shape = area.shape
    area_shape_width = area_shape[1]
    area_shape_height = area_shape[0]
    return abs(area_shape_width - area_shape_height) < 10

def load_grid(file_name: str) -> cv2.Mat:
    image = cv2.imread(file_name)
    if image is None:
        raise ValueError(f"Could not load image from path: {file_name}")
    grid = get_area_of_interest(image)
    if not is_valid_area(grid):
        raise ValueError("The loaded area of interest is not valid")
    return grid


def acquire_grid() -> cv2.Mat:
    while True:
        screenshot = pyautogui.screenshot()
        screenshot.save(TEMP_FILE)
        image = cv2.imread(TEMP_FILE)
        if image is None:
            raise ValueError(f"Could not load image from path: {TEMP_FILE}")

        grid = get_area_of_interest(image)

        if is_valid_area(grid):
            return grid


def get_area_of_interest(image: cv2.Mat) -> cv2.Mat:
    processed = image.copy()
    # 2. Preprocessing
    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    dump_image("gray.png", gray)
    dump_image("blurred.png", blurred)
    dump_image("thresh.png", thresh)


    # 3. Contour Detection
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    cv2.drawContours(processed, contours, -1, (0, 255, 0), 2)
    dump_image('contours.png', processed)

    # 4. Grid Identification
    if not contours:
        raise ValueError("No contours found in the image")
    grid_contour = contours[0]
    perimeter = cv2.arcLength(grid_contour, True)
    approx = cv2.approxPolyDP(grid_contour, 0.02 * perimeter, True)
    cv2.drawContours(processed, contours, 0, (0, 0, 255), 7)
    xx = [pt[0][0] for pt in approx]
    yy = [pt[0][1] for pt in approx]
    tl = (min(xx), min(yy))
    br = (max(xx), max(yy))
    cropped_image = image[tl[1]:br[1], tl[0]:br[0]]
    dump_image("crop.png", cropped_image)
    return cropped_image

