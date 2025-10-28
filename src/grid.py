class Grid:
    def __init__(self, cell_size: int, cell_count: int = 6):
        self._cell_size = cell_size
        self._cell_count = cell_count
        self._data = [['  ' for _ in range(cell_count)] for _ in range(cell_count)]

    def set_from_pixel(self, row: int, column: int, value: str):
        r = row // self._cell_size
        c = column // self._cell_size
        print(f">>> ({r}, {c}) = {value} - {self._cell_size}")
        self._data[r][c] = value

    def find(self, value: str):
        for r in range(6):
            for c in range(6):
                if self._data[r][c] == value:
                    return r, c
        return None, None

    def as_int_array(self):
        result = []
        for line in self._data:
            result_line = []
            for x in line:
                try:
                    result_line.append(int(x))
                except ValueError:
                    result_line.append(None)
            result.append(result_line)
        return result

    def pretty_print(self):
        for line in self._data:
            print(" +" + "----+"*self._cell_count)
            print(" | " + " | ".join(str(x) for x in line) + " | ")
        print(" +" + "----+"*self._cell_count)

if __name__ == "__main__":
    grid = Grid()
    grid.pretty_print()