import cv2

from utils import dump_image


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

