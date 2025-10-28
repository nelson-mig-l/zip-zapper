import cv2
from cv2 import Mat
from utils import dump_image


TEMPLATES = [
    "01", "02", "03", "04", "05", "06", '07', "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19"
]

TEMPLATE_SIZE = 53

def find_templates(image: Mat, mock_image: Mat, max_number: int, avg_diameter: int) -> dict[str, tuple[int, int]]:
    """
    Find all templates in the given image.
    Args:
        image (Mat):
            The image to search for templates.
        mock_image (Mat):
            The image to draw debug rectangles on.
        max_number (int):
            The maximum number of templates to find.
        avg_diameter (int):
            The average diameter of the circles in the image.
    Returns:
        dict[str, tuple[int, int]]:
            A dictionary mapping template IDs to their (x, y) coordinates in the image.
            Example: { "01": (x1, y1), "02": (x2, y2), ... }
    """
    search_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = {}
    for template_id in TEMPLATES[:max_number]:
        template_path = f"templates/{template_id}.png"
        template = cv2.cvtColor(cv2.imread(template_path), cv2.COLOR_BGR2GRAY)
        if abs(avg_diameter - TEMPLATE_SIZE) > 5:
            print("Resizing template", template_id, "from", TEMPLATE_SIZE, "to", avg_diameter+3)
            scale_factor = avg_diameter / TEMPLATE_SIZE
            new_size = (int(template.shape[1] * scale_factor), int(template.shape[0] * scale_factor))
            template = cv2.resize(template, new_size)
        x, y = _find_template(search_image, mock_image, template, template_id)
        results[template_id] = (x, y)
    dump_image("template_matches.png", mock_image)
    return results

def _find_template(search: Mat, debug: Mat, template: Mat, template_id: str) -> tuple[int, int]:
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    cv2.rectangle(debug, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 255), 2)
    cv2.rectangle(search, max_loc, (max_loc[0] + w, max_loc[1] + h), (255, 255, 255), -1)
    cv2.putText(debug, template_id, (max_loc[0]+10, max_loc[1]+35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
    return max_loc[0], max_loc[1]

# https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
# We could also detect multiple instances of the same template using thresholding:
# threshold = 0.8
# loc = np.where(res >= threshold)
# for pt in zip(*loc[::-1]):
#     x = pt[0]
#     y = pt[1]
#     cv2.rectangle(debug, (x, y), (x+w, y+h), (0, 255, 255), 2)
#     cv2.putText(debug, template_id, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
