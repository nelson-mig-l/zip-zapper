import cv2
from cv2 import Mat
from utils import dump_image
# https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html

TEMPLATES = [
    "01", "02", "03", "04", "05", "06", '07', "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18",
]

# def find_templates(image: Mat):
#     t_04 = cv2.cvtColor(cv2.imread("templates/04.png"), cv2.COLOR_BGR2GRAY)
#     w, h = t_04.shape[::-1]
#     debug_image = image.copy()
#     search_image = cv2.cvtColor(debug_image, cv2.COLOR_BGR2GRAY)
#     res = cv2.matchTemplate(search_image, t_04, cv2.TM_CCOEFF)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#     print(cv2.minMaxLoc(res))
#
#     cv2.rectangle(debug_image, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,255,0), 2)
#     dump_image("template_match_04.png", debug_image)

def find_templates(image: Mat) -> dict[str, tuple[int, int]]:
    debug_image = image.copy()
    search_image = cv2.cvtColor(debug_image, cv2.COLOR_BGR2GRAY)
    results = {}
    for template_id in TEMPLATES:
        x, y = _find_template(search_image, debug_image, template_id)
        results[template_id] = (x, y)
    dump_image("template_matches.png", debug_image)
    return results

def _find_template(search: Mat, debug: Mat, template_id: str, threshold: float = 0.8) -> tuple[int, int]:
    template_path = f"templates/{template_id}.png"
    template = cv2.cvtColor(cv2.imread(template_path), cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
    # res = cv2.matchTemplate(search, template, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    cv2.rectangle(debug, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 255), 2)
    cv2.putText(debug, template_id, (max_loc[0]+5, max_loc[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
    return max_loc[0], max_loc[1]

# def _find_template(image: Mat, template_path: str, threshold: float = 0.8):
#     template = cv2.cvtColor(cv2.imread(template_path), cv2.COLOR_BGR2GRAY)
#     w, h = template.shape[::-1]
#     search_image = image.copy()
#     res = cv2.matchTemplate(cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
#     loc = cv2.minMaxLoc(res)
#     print(f"Template {template_path} minMaxLoc: {loc}")
#     match_locations = []
    # yloc, xloc = (res >= threshold).nonzero()
    # for (x, y) in zip(xloc, yloc):
    #     match_locations.append((x, y))
    #     cv2.rectangle(search_image, (x, y), (x + w, y + h), (0,255,0), 2)
    # dump_image(f"template_match_{search(template_path, r'(\d{2})').group(1)}.png", search_image)
    # return match_locations
