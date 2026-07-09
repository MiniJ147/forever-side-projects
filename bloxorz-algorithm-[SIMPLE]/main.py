import sys
from collections import deque

def tuple_sub(a: tuple(int, int), b: tuple(int, int)) -> tuple(int,int):
    return (a[0]-b[0], a[1]-b[1])

# |===== MAP STUFF =====|
# cell typing
NODE_NORMAL = 0
NODE_SPACE = 1
NODE_START = 2
NODE_GOAL = 3
NODE_RED = 4

node_type_map = {
    '#': NODE_NORMAL,
    '.': NODE_SPACE,
    'S': NODE_START,
    'G': NODE_GOAL,
    'R': NODE_RED
}

EDGE_BUF = 3

class Node:
    def __init__(self, x, y, type, chr):
        self.x = x
        self.y = y
        self.type = type
        self.chr = chr

def create_map(map_name: str):
    graph = []
    start = (-1, -1)
    goal = (-1,-1)
    with open(map_name, "r") as file:
        # reading lines
        lines = []; width = 0
        for line in file:
            line = line.strip()
            width = max(width, len(line))
            lines.append(line)

        # adjust width / height for map edges
        # push by 2 extra on each side
        width += EDGE_BUF * 2 
        height = len(lines) + EDGE_BUF * 2
    
        # turning the map square
        mp = ["." * width for _ in range(EDGE_BUF)] # push top
        for line in lines:
            new_line = ["."] * width
            for i in range(len(line)):
                new_line[i + EDGE_BUF] = line[i]
            mp.append("".join(new_line))
        for _ in range(EDGE_BUF): mp.append("." * width) # push below

        print("LOADED MAP: ", map_name)
        for i, row in enumerate(mp):
            print(i,"\t",row)

        # constructing graph
        for y in range(height):
            row = []
            for x in range(width):
                node_type = node_type_map[mp[y][x]]
                if node_type == NODE_GOAL: 
                    goal = (x,y)
                elif node_type == NODE_START:
                    start = (x, y)
                row.append(
                    Node(x, y, node_type, mp[y][x]))
            graph.append(row)                
    return graph, start, goal

# |===== PLAYER STUFF =====|
PLAYER_ORIEN_STRAIGHT = 0 # straight up in the air
# on the side facing
PLAYER_ORIEN_UP = 1 
PLAYER_ORIEN_DOWN = 2 
PLAYER_ORIEN_LEFT = 3 
PLAYER_ORIEN_RIGHT = 4

# returns (ORIEN, POS)
PLAYER_MOVES_FSM = {
    PLAYER_ORIEN_STRAIGHT: [
        (PLAYER_ORIEN_UP, (0,-1)), (PLAYER_ORIEN_RIGHT, (1,0)),
        (PLAYER_ORIEN_DOWN, (0,1)), (PLAYER_ORIEN_LEFT, (-1,0))
    ],
    PLAYER_ORIEN_UP: [
        (PLAYER_ORIEN_UP, (1,0)), (PLAYER_ORIEN_UP, (-1,0)),
        (PLAYER_ORIEN_STRAIGHT, (0,1)), (PLAYER_ORIEN_STRAIGHT, (0,-2))
    ],
    PLAYER_ORIEN_DOWN: [
        (PLAYER_ORIEN_DOWN, (1,0)), (PLAYER_ORIEN_DOWN, (-1,0)),
        (PLAYER_ORIEN_STRAIGHT, (0,2)), (PLAYER_ORIEN_STRAIGHT, (0,-1))
    ],
    PLAYER_ORIEN_RIGHT: [
        (PLAYER_ORIEN_STRAIGHT, (2,0)), (PLAYER_ORIEN_STRAIGHT, (-1,0)),
        (PLAYER_ORIEN_RIGHT, (0,1)), (PLAYER_ORIEN_RIGHT, (0,-1))
    ],
    PLAYER_ORIEN_LEFT: [
        (PLAYER_ORIEN_STRAIGHT, (1,0)), (PLAYER_ORIEN_STRAIGHT, (-2,0)),
        (PLAYER_ORIEN_LEFT, (0,1)), (PLAYER_ORIEN_LEFT, (0,-1))
   ]
}

PLAYER_ORIEN_STR = {
    PLAYER_ORIEN_STRAIGHT: "STRAIGHT",
    PLAYER_ORIEN_UP: "UP",
    PLAYER_ORIEN_DOWN: "DOWN",
    PLAYER_ORIEN_LEFT: "LEFT",
    PLAYER_ORIEN_RIGHT: "RIGHT",
}

PLAYER_ORIEN_BLACKLIST = {
    PLAYER_ORIEN_STRAIGHT: {NODE_RED, NODE_SPACE},
    PLAYER_ORIEN_UP: {NODE_SPACE},
    PLAYER_ORIEN_DOWN: {NODE_SPACE},
    PLAYER_ORIEN_LEFT: {NODE_SPACE},
    PLAYER_ORIEN_RIGHT: {NODE_SPACE},
}

def validate_move(map, x, y, orientation):
    """
    Takes in the base position and the current orientation.
    Verifies that his base and orientation can exist 
    """
    def strip_verify(strip, blacklist):
        for node in strip:
            if node.type in blacklist:
                return False
        return True
    
    blacklist = PLAYER_ORIEN_BLACKLIST[orientation]
       
    if orientation == PLAYER_ORIEN_STRAIGHT:
        return strip_verify([map[y][x]], blacklist) 

    if orientation == PLAYER_ORIEN_UP:
        return strip_verify([map[y][x], map[y-1][x]], blacklist)  
    if orientation == PLAYER_ORIEN_DOWN:
        return strip_verify([map[y][x], map[y+1][x]], blacklist)

    if orientation == PLAYER_ORIEN_LEFT:
        return strip_verify([map[y][x], map[y][x-1]], blacklist)
    if orientation == PLAYER_ORIEN_RIGHT:
        return strip_verify([map[y][x], map[y][x+1]], blacklist)
    
    return False

def algo(map, start, goal):
    start_state = (PLAYER_ORIEN_STRAIGHT, start)
    vis = {start_state}; q = deque([start_state])

    par_map = {}
    # NOTE: all elements in the q are considered valid
    while q:
        orien, pos = q.popleft()
        x, y = pos

        if pos == goal and orien == PLAYER_ORIEN_STRAIGHT: # reached end
            path = [] 
            cur = (orien, pos)
            while True:
                path.append((PLAYER_ORIEN_STR[cur[0]], cur[1], cur[0]))
                if cur not in par_map:
                    break
                cur = par_map[cur]

            i = 0
            prev = path[-1][1]
            while path:
                orien, pos, _ = path.pop()
                dx, dy = tuple_sub(pos,prev)
                print(i,end=" "); i += 1
                if dx > 0: print(">")
                elif dx < 0: print("<")
                elif dy > 0: print("v")
                elif dy < 0: print("^")
                prev = pos
                # print(orien, pos)
            return True

        moves = PLAYER_MOVES_FSM[orien]
        for move in moves:
            new_orien = move[0]; dx, dy = move[1]
            state = (new_orien, (x+dx, y+dy))
            if validate_move(map, x+dx, y+dy, new_orien) and state not in vis:
                vis.add((orien, pos)) # visit node
                par_map[state] = (orien, (x,y))
                q.append(state)

    return False

def main(map_name: str): 
    print("Hello Bloxorz!")
    mp, start, goal = create_map(map_name)
    ms = start == (-1,-1); mg = goal == (-1, -1)
    if ms or mg:
        print(f"MAP ERROR MISSING: [START]={ms}, [GOAL]={mg}")
        return
    print(algo(
        map = mp,
        start=start,
        goal=goal 
    ))

if __name__ == "__main__":
    main(sys.argv[1])