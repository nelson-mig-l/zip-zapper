import time

import cv2
import numpy as np
import pyautogui

from area_of_interest import get_area_of_interest
from utils import dump_image
from grid import Grid
from templates import find_templates
from zip_zap import zipSolver

def resolve_key_stroke(c_x: int, c_y: int, n_x: int, n_y: int) -> str:
    if n_x == c_x and n_y == c_y - 1:
        return "UP"
    elif n_x == c_x and n_y == c_y + 1:
        return "DOWN"
    elif n_x == c_x - 1 and n_y == c_y:
        return "LEFT"
    elif n_x == c_x + 1 and n_y == c_y:
        return "RIGHT"
    else:
        raise ValueError(f"Invalid move from ({c_x}, {c_y}) to ({n_x}, {n_y})")

if __name__ == "__main__":
    print("Starting...")

    while True:
        screenshot = pyautogui.screenshot()
        screenshot.save("screen_shot.png")

        image = cv2.imread("screen_shot.png")
        # image = cv2.imread("screen.png")
        if image is None:
            raise ValueError("Could not load image from path: {}".format("screen.png"))
        print("Extracting area of interest...")
        cropped_image = get_area_of_interest(image)
        print("Gathering cropped image info...")
        cropped_image_shape = cropped_image.shape
        cropped_image_width = cropped_image_shape[1]
        cropped_image_height = cropped_image_shape[0]
        cv2.imwrite("crop.png", cropped_image)
        grid_size = np.average(cropped_image_shape[:2])
        cell_width, cell_height = (cropped_image_width/6, cropped_image_height/6)
        cell_size = grid_size / 6
        print(f"Grid size = {(cropped_image_width, cropped_image_height)} -> {grid_size}")
        print(f"Cell size: {(cell_width, cell_height)} -> {cell_size}")

        if abs(cell_width - cell_height) < 10:
            break
        print(f"{abs(cell_width - cell_height)} Retrying...")
    print("Success")

    # HACK
    cropped_image_width = 486
    cropped_image_height = 486
    cropped_image = cv2.resize(cropped_image, (486, 486))
    cropped_image_shape = cropped_image.shape
    cell_width, cell_height = (cropped_image_width / 6, cropped_image_height / 6)
    grid_size = np.average(cropped_image_shape[:2])
    cell_size = grid_size / 6
    print(f">>> Grid size = {(cropped_image_width, cropped_image_height)} -> {grid_size}")
    print(f">>> Cell size: {(cell_width, cell_height)} -> {cell_size}")
    dump_image("xxx.png", cropped_image)


    grid = Grid(int(cell_size))

    # Draw grid for visualization
    mock = cropped_image.copy()
    w, h = (cropped_image_width, cropped_image_height)
    for i in range(0,7):
        # horizontal lines
        cv2.line(mock, (0, i * h // 6), (w, i * h // 6), (255,0,0), 10)
        # vertical lines
        cv2.line(mock, (i * w // 6, 0), (i * w // 6, h), (255,0,0), 10)
    dump_image("grid.png", mock)


    # 5. Circle Detection
    print("Detecting circles...")
    circles = cv2.HoughCircles(
        cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY),
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=cell_size/2,  # distance between centers
        param1=50,
        param2=30,
        minRadius=20, # minimum radius
        maxRadius=30  # maximum radius
    )
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"Found {len(circles[0, :])} circles")
        for i in circles[0, :]:
            cv2.circle(mock, (i[0], i[1]), i[2], (0, 0, 255), -1)
            grid.set_from_pixel(i[1], i[0], "XX")

    dump_image("circles.png", mock)
    grid.pretty_print()

    templates = find_templates(cropped_image)
    for template_id, (x, y) in templates.items():
        grid.set_from_pixel(y, x, template_id)

    #HACK
    r, c = grid.find("XX")
    if r is not None and c is not None:
        grid._data[r][c] = '01'

    grid.pretty_print()
    zip_array = grid.as_int_array()


    key_strokes = []
    print(zip_array)
    barrier_bricks = []
    solved_grid, path = zipSolver(zip_array, barrier_bricks)
    print(path)
    c_y, c_x = path[0]
    for n_y, n_x in path[1:]:
        print(f"{n_x} {n_y}")
        cv2.line(
            mock,
            (int(c_x * cell_width + cell_width // 2), int(c_y * cell_height + cell_height // 2)),
            (int(n_x * cell_width + cell_width // 2), int(n_y * cell_height + cell_height // 2)),
            (0, 255, 0),
            10,
        )
        key_strokes.append(resolve_key_stroke(c_x, c_y, n_x, n_y))
        c_x = n_x
        c_y = n_y


    dump_image("solved_path.png", mock)
    print("Solved grid:")
    print(solved_grid)
    print(key_strokes)

    # time.sleep(5)  # Give yourself 5 seconds to switch to a target window
    for key in key_strokes:
        print(f"Pressing key: {key}")
        pyautogui.press(key)
        # time.sleep(0.005)  # Small delay between key presses
