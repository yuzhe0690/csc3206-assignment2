class Node:
  def __init__(self, obstacle_map=None, x=None, y=None, cost=0, energy=1, heuristic=0):
    self.obstacle_map = obstacle_map
    self.x = x
    self.y = y
    self.cost = cost
    self.energy = energy
    self.heuristic = heuristic
    self.neighbors = []
    
    def add_neighbors(self, neighbors):
        self.neighbors.extend(neighbors)

def is_blocked(x, y, obstacle_map):
    return obstacle_map[x][y] == 1

def is_valid(x, y, state_space):
    return x >= 0 and x < len(state_space) and y >= 0 and y < len(state_space[0])

def get_positions(state_space, node_type):
    list = []
    for i in range(len(state_space)):
        for j in range(len(state_space[0])):
            if state_space[i][j] == node_type:
                list.append((i, j))
    return list

def heuristic(x, y, node, energy):
    return (abs(x - node[0]) + abs(y - node[1])) * energy

def get_neighbors(x, y, node, state_space, obstacle_map):
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if is_valid(x + i, y + j, state_space) and not is_blocked(x + i, y + j, obstacle_map):
                neighbors.append(Node(obstacle_map,x+i,y+j,1,1,heuristic(x+i, y+j,node,1)))
    return neighbors

def append_and_sort(frontier, node):
    duplicated = False
    removed = False
    for i, f in enumerate(frontier):
        if f.x == node.x and f.y == node.y:
            duplicated = True
            if f.heuristic > node.heuristic:
                del frontier[i]
                removed = True
                break    
        if (not duplicated) or removed:
            insert_index = len(frontier)
            for i, f in enumerate(frontier):
                if f.cost > node.cost:
                    insert_index = i
                    break
        frontier.insert(insert_index, node)
    return frontier

def gbfs(state_space, obstacle_map, start):
    frontier = []
    explored = []
    treasures = get_neighbors(state_space,'Treasure')
    total_cost = 0
    frontier.append(Node(obstacle_map=obstacle_map, x=0, y=0, cost=0, energy=1, heuristic=0))

    while len(treasures) >= 0:
        # goal test at expansion
        if frontier[0].state == treasures[0]:
            break
        # expand the first in the frontier
        children = get_neighbors(frontier[0].x, frontier[0].y, state_space, obstacle_map)
        # add children list to the expanded node
        frontier[0].add_neighbors(children)
        # add to the explored list
        explored.append(frontier[0])
        # remove the expanded frontier
        del frontier[0]
        # add children to the frontier
        for child in children:
        # check if a node was expanded or generated previously
            if not (child.x in [e.x for e in explored] and child.y in [e.y for e in explored]):        
                frontier = append_and_sort(frontier, child)
            print("Explored:", [(e.x,e.y) for e in explored])
            print("Frontier:", [((f.x,f.y), f.heuristic) for f in frontier])
            print("Children:", [c.state for c in children])
            print("")

    return total_cost

if __name__ == "__main__":  
    # state space and step cost definition
    state_space = [
        ['Empty','Empty','Trap1','Treasure'],
        ['Obstacle','Empty','Emmpty','Trap2'],
        ['Treasure','Reward2','Obstacle','Empty'],
        ['Trap4','Empty','Empty','Reward1']
    ]

    obstacle_map =[
        [0,0,0,0],
        [1,0,0,0],
        [0,0,1,0],
        [0,0,0,0]
    ]

