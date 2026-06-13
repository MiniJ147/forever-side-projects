# prototype for wave function collapse algorithm
# Goal: generate random islands
import random

MAP_WIDTH = 16; MAP_HEIGHT = 16

CELL_EMPTY = 0
CELL_SAND = 1
CELL_WATER = 2
CELL_GRASS = 3
CELL_MOUNTAIN = 4

CELL_OPTIONS = {
    CELL_EMPTY: set([CELL_SAND, CELL_WATER, CELL_GRASS, CELL_MOUNTAIN]),
    CELL_WATER: set([CELL_SAND, CELL_WATER]),
    CELL_SAND: set([CELL_SAND, CELL_WATER, CELL_GRASS]),
    CELL_GRASS: set([CELL_SAND, CELL_GRASS, CELL_MOUNTAIN]),
    CELL_MOUNTAIN: set([CELL_GRASS, CELL_MOUNTAIN])
}
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'

CELL_CHAR = {
    CELL_EMPTY: ".",
    CELL_GRASS: "\033[32m#",
    CELL_SAND: "\033[33m#",   
    CELL_WATER: "\033[34m~",
    CELL_MOUNTAIN: "\033[37m^"
}

CELL_ALL_LIST = CELL_OPTIONS.keys()
MAX_ENTROPY = len(CELL_ALL_LIST)

class Cell:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.type = CELL_EMPTY
        self.entropy = MAX_ENTROPY - 1
        self.options = set(CELL_ALL_LIST)
        self.options.remove(self.type)

    def get_entropy(self):
        return self.entropy
    
    def reduce_entropy(self, update_cell):
        """
        reduce_entropy (self, update_cell): takes in a new cell and calculates new entropy
        """
        if self.entropy == 0: return 0
        self.options = self.options & CELL_OPTIONS[update_cell]
        self.entropy = len(self.options)
        return self.entropy
        
    def collapse(self): 
        self.type = list(self.options)[random.randint(0,self.entropy-1)] # pick cell
        self.entropy = 0 # collapse entropy
        return self.type # return new option

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.data = [[Cell(x,y) for x in range(width)] for y in range(height)]
        self.iter_window = set([self.data[height//2][width//2]]) # pull first into window

    # iterates the map by one cell, and return True if it was successful
    # if false then no more collapsing can happen
    # random search, extra calculations but might be cooler?
    def can_iter(self):
        return len(self.iter_window) > 0

    def iter(self):
        mi = MAX_ENTROPY; iw = self.iter_window; iw_len = len(iw)
        if iw_len == 0: return False
        choices = []
        for c in iw:
            if c.entropy == 0: 
                continue
            if c.entropy < mi:
                mi = c.entropy
                choices = [c]
            elif c.entropy == mi: 
                choices.append(c)
        if len(choices) == 0:
            return False

        c = choices[random.randint(0, len(choices)-1)]; iw.remove(c)
        x = c.x; y = c.y; nc = c.collapse()

        if x-1 >= 0: 
            _c = self.data[y][x-1]
            _c.reduce_entropy(nc)
            iw.add(_c)
        if x+1 < self.width: 
            _c = self.data[y][x+1]
            _c.reduce_entropy(nc)
            iw.add(_c)
        if y-1 >= 0: 
            _c = self.data[y-1][x]
            _c.reduce_entropy(nc)
            iw.add(_c)
        if y+1 < self.height: 
            _c = self.data[y+1][x]
            _c.reduce_entropy(nc)   
            iw.add(_c)

        return True
        
    def print_map(self, type="entropy"):
        for row in self.data:
            for cell in row:
                if type=="entropy":
                    print(cell.entropy,end=" ")
                elif type=="type":
                    print(cell.type, end=" ")
                else:
                    print(CELL_CHAR[cell.type],end=" ")
            print()
        print("\033[0m")

def main():
    m = Map(MAP_WIDTH, MAP_HEIGHT)
    while m.iter():
        continue
    m.print_map("render")



if __name__ == "__main__":
    main()