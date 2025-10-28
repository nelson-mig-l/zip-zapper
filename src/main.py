import cv2
import numpy as np

from area_of_interest import load_grid
from keyboard import keyboard_action
from utils import dump_image
from grid import Grid
from templates import find_templates
from zip_zap import zipSolver

NORMALIZED_CELL_SIZE = 80

type Point = tuple[float, float]
type Line = tuple[Point, Point]

def distance_point_to_point(p1: Point, p2: Point) -> float:
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def is_approx_equal(a: Line, b: Line, tolerance: float) -> bool:
    start_distance = distance_point_to_point(a[0], b[0])
    end_distance = distance_point_to_point(a[1], b[1])
    return (start_distance < tolerance) and (end_distance < tolerance)


def find_unique_lines(lines, tolerance):
    duplicated = []
    seen_values = []
    for line in lines:
        for seen in seen_values:
            if is_approx_equal(line, seen, tolerance):
                duplicated.append(line)
                print("Duplicate line:", line, " -> ", seen)
                break
        seen_values.append(line)
    return set(lines) - set(duplicated)


if __name__ == "__main__":
    print("Starting...")

    # 1. Acquire Image
    print("Acquiring image...")
    # grid_image = acquire_grid()
    grid_image = load_grid("examples/screen1.png")
    dump_image("grid_raw.png", grid_image)

    # 2. Row and columns detection
    edges = cv2.Canny(cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY), 50, 150, apertureSize=3)
    hough_lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    lines = []
    for hough_line in hough_lines:
        rho, theta = hough_line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        print((x1, y1),(x2, y2))
        lines.append(((x1, y1),(x2, y2)))
    print(f"Found {len(lines)} lines")
    unique_lines = find_unique_lines(lines, tolerance=25)
    print(f"Found {len(unique_lines)} clean lines")
    cells_in_axis = len(unique_lines) // 2 + 1
    print(f"Cells in axis: {cells_in_axis}")

    mock_grid_image = grid_image.copy()
    for out_lines in unique_lines:
        (x1, y1), (x2, y2) = out_lines
        cv2.line(mock_grid_image, (x1, y1), (x2, y2), (255, 0, 0), 7)
    for line in lines:
        (x1, y1), (x2, y2) = line
        cv2.line(mock_grid_image, (x1, y1), (x2, y2), (255, 255, 0), 1)
    dump_image("grid_lines.png", mock_grid_image)

    # 3. Normalize IMAGE size
    normalized_size = (cells_in_axis * NORMALIZED_CELL_SIZE, cells_in_axis * NORMALIZED_CELL_SIZE)
    grid_image = cv2.resize(grid_image, normalized_size)
    dump_image("grid_normalized.png", grid_image)
    mock_grid_image = cv2.resize(mock_grid_image, normalized_size)

    grid = Grid(int(NORMALIZED_CELL_SIZE), cells_in_axis)

    # 5. Circle Detection
    print("Detecting circles...")
    circles = cv2.HoughCircles(
        cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY),
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=NORMALIZED_CELL_SIZE/2,  # distance between centers
        param1=50,
        param2=30,
        minRadius=NORMALIZED_CELL_SIZE//4, # minimum radius
        maxRadius=NORMALIZED_CELL_SIZE//3  # maximum radius
    )
    diameters = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"Found {len(circles[0, :])} circles")
        for i in circles[0, :]:
            cv2.circle(mock_grid_image, (i[0], i[1]), i[2], (0, 0, 255), -1)
            cv2.putText(mock_grid_image, str(i[2]*2), (i[0]-10, i[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            grid.set_from_pixel(i[1], i[0], "XX")
            diameters.append(i[2]*2)
    else:
        print("No circles found")

    dump_image("circles.png", mock_grid_image)
    grid.pretty_print()

    # find numbers
    templates = find_templates(grid_image, mock_grid_image, len(circles[0, :]), sum(diameters) // len(diameters))
    for template_id, (x, y) in templates.items():
        grid.set_from_pixel(y, x, template_id)

    #HACK
    # r, c = grid.find("XX")
    # if r is not None and c is not None:
    #     grid._data[r][c] = '01'

    grid.pretty_print()
    zip_array = grid.as_int_array()

    barrier_bricks = []
    # detect barriers bricks
    for row in range(0, cells_in_axis):
        for col in range(0, cells_in_axis):
            position = (col * NORMALIZED_CELL_SIZE, row * NORMALIZED_CELL_SIZE)
            cv2.circle(mock_grid_image, position, 5, (0, 255, 0), 2)
            # Horizontal ===============================================
            pt1 = (position[0] + 10, position[1])
            pt2 = (position[0] + NORMALIZED_CELL_SIZE - 10, position[1])
            # cv2.line(mock_grid_image, pt1, pt2, (0, 255, 255), 3)

            # [y, y+h, x, x+w]
            xi = position[0] + 10
            xf = position[0] + NORMALIZED_CELL_SIZE - 10
            yi = position[1] - 5
            yf = position[1] + 5

            h_roi = grid_image[yi:yf, xi:xf]
            px_val_cnt = np.sum(h_roi)
            if px_val_cnt < 150000:
                cv2.rectangle(mock_grid_image, (xi, yi), (xf, yf), (0, 0, 255), -1)
                cv2.putText(mock_grid_image, f"{col}_{row}", (xi, yi + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),2)
                print(f">>> {row}, {col} = {px_val_cnt}")
                if row > 0:
                    # print("Adding horizontal barrier:", (col, row))
                    # brick = {(col, row - 1), (col, row)}
                    brick = {(row-1, col), (row, col)}
                    # print(brick)
                    barrier_bricks.append(brick)
            else:
                cv2.rectangle(mock_grid_image, (xi, yi), (xf, yf), (0, 255, 0), 3)
            # cv2.putText(mock_grid_image, f"{px_val_cnt}", (xi, yi+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
            # cv2.putText(mock_grid_image, f"{r}_{c}", (xi, yi), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            # mock_grid_image[yi:yf, xi:xf] = h_roi

            # show_image(f"roi r{r} c{c}", h_roi)
            # Vertical ================================================
            xi = position[0] - 5
            yi = position[1] + 10
            xf = position[0] + 5
            yf = position[1] + NORMALIZED_CELL_SIZE - 10

            v_roi = grid_image[yi:yf, xi:xf]
            if np.sum(v_roi) < 150000:
                # barrier_bricks.append(((r, c), (r, c+1)))
                cv2.rectangle(mock_grid_image, (xi, yi), (xf, yf), (0, 0, 255), -1)
                cv2.putText(mock_grid_image, f"{col}_{row}", (xi + 5, yi + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                # print(f">>> {r}, {c} = {px_val_cnt}")
                # barrier_bricks.append({(c, r), (c, r+1)})

                brick = {(row, col-1), (row, col)}
                if col > 0:
                    print("Adding horizontal barrier:", (col, row))
                    print(brick)
                    barrier_bricks.append(brick)
            else:
                cv2.rectangle(mock_grid_image, (xi, yi), (xf, yf), (0, 255, 0), 3)



    dump_image("barriers.png", mock_grid_image)


    solved_grid, path = zipSolver(zip_array, barrier_bricks)
    print(solved_grid)
    print(path)
    # sys.exit(0)
    c_y, c_x = path[0]
    for n_y, n_x in path[1:]:
        print(f"{n_x} {n_y}")
        cv2.line(
            mock_grid_image,
            (int(c_x * NORMALIZED_CELL_SIZE + NORMALIZED_CELL_SIZE // 2), int(c_y * NORMALIZED_CELL_SIZE + NORMALIZED_CELL_SIZE // 2)),
            (int(n_x * NORMALIZED_CELL_SIZE + NORMALIZED_CELL_SIZE // 2), int(n_y * NORMALIZED_CELL_SIZE + NORMALIZED_CELL_SIZE // 2)),
            (0, 255, 0),
            10,
        )
        c_x = n_x
        c_y = n_y
    dump_image("solved_path.png", mock_grid_image)
    # sys.exit(0)

    keyboard_action(path)
