# zip-zapper :zap:

A quick'n'dirty lnkd.in/zip solver.

## How?

### Get grid
1. get screenshot
1. `cv2.findContours` + `cv2.approxPolyDP` = "grid crop"
1. Is it a valid grid? _"Is is a square grid?"_
    1. No - repeat
    1. Yes - return crop

### Get size of grid
1. detect lines, horizontal and vertical (`cv2.HoughLinesP`)
2. de-duplicate lines
3. count lines -> calculate cell count

### Normalize grid size
So that cell size is a known constant for the rest of the algorithm.

### Find numbers in grid
1. `cv2.HoughCircles`
1. Template matching to images (`templates/*.png`)
2. take into account that circle radius may vary.
   Adjust template size is needed.

### Detect barriers
1. get ROIs for cell borders
2. count black pixels and guess if barrier or not

### Solve
1. https://medium.com/@mvenkatashivaditya/linkedin-zip-puzzle-solver-python-953be08daab3
1. Get keystrokes necessary to travel the path
1. Replay keystrokes

