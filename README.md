# zip-zapper :zap:

A quick'n'dirty lnkd.in/zip solver.

## How?

### Get grid
1. get screenshot
1. `cv2.findContours` + `cv2.approxPolyDP` = "grid crop"
1. Is it a valid grid? _"Is is a square grid?"_
    1. No - repeat
    1. Yes - return crop

### :poop:
1. dirty stuff to clean up

### Find numbers in grid
1. `cv2.HoughCircles`
1. Template matching to images (`templates/*.png`)

### :poop:
1. more dirty stuff to clean up

### Solve
1. https://medium.com/@mvenkatashivaditya/linkedin-zip-puzzle-solver-python-953be08daab3
1. Get keystrokes necesssary to travel the path
1. Replay keystrokes

