import pyautogui


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

def keyboard_action(path):
    key_strokes = []
    print(path)
    c_y, c_x = path[0]
    for n_y, n_x in path[1:]:
        print(f"{n_x} {n_y}")
        key_strokes.append(resolve_key_stroke(c_x, c_y, n_x, n_y))
        c_x = n_x
        c_y = n_y
    print(key_strokes)

    # time.sleep(5)  # Give yourself 5 seconds to switch to a target window
    for key in key_strokes:
        print(f"Pressing key: {key}")
        pyautogui.press(key)
        # time.sleep(0.005)  # Small delay between key presses
