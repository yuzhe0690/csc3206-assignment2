import random

class VirtualWorld:
    def __init__(self, grid, traps, rewards, entry):
        # Initialize the virtual world with the grid, traps, rewards, and entry point
        self.grid = grid
        self.traps = traps
        self.rewards = rewards
        self.entry = entry
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.treasure_positions = self.get_positions('Treasure')
        self.visited = set()
        self.collected_treasures = 0
        self.position_tracker = []

    def get_positions(self, item_type):
        # Get the positions of a specific item type in the grid
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == item_type:
                    positions.append((r, c))
        return positions

    def count_elements(self):
        # Count the occurrences of each element type in the grid
        counts = {
            'Treasure': len(self.get_positions('Treasure')),
            'Reward1': len(self.get_positions('Reward1')),
            'Reward2': len(self.get_positions('Reward2'))
        }
        for trap, effect in self.traps.items():
            counts[trap] = sum(row.count(trap) for row in self.grid)
        counts['Obstacle'] = sum(row.count('Obstacle') for row in self.grid)
        counts['Empty'] = sum(row.count('Empty') for row in self.grid)
        return counts

    def in_bounds(self, r, c):
        # Check if a position is within the bounds of the grid
        return 0 <= r < self.rows and 0 <= c < self.cols

    def apply_effects(self, position, energy, steps):
        # Apply the effects of traps or rewards encountered at a position
        cell = self.grid[position[0]][position[1]]
        effect = None
        applied_effect_name = None

        if cell in self.traps:
            # If the cell is a trap, apply the corresponding effect
            effect = self.traps[cell]
            applied_effect_name = f"Trap '{cell}' effect '{effect}'"
            if effect == 'increase_gravity':
                energy *= 2
            elif effect == 'decrease_speed':
                steps *= 2
            elif effect == 'move_two_cells':
                for dr, dc in [(2, 0), (0, 2), (-2, 0), (0, -2)]:
                    new_r, new_c = position[0] + dr, position[1] + dc
                    if self.in_bounds(new_r, new_c):
                        position = (new_r, new_c)
                        break
            elif effect == 'remove_treasures':
                self.treasure_positions = []
        elif cell in self.rewards:
            # If the cell is a reward, apply the corresponding effect
            effect = self.rewards[cell]
            applied_effect_name = f"Reward '{cell}' effect '{effect}'"
            if effect == 'decrease_gravity':
                energy /= 2
            elif effect == 'increase_speed':
                steps /= 2

        self.position_tracker.append((position, applied_effect_name))
        return position, energy, steps

    def heuristic(self, position):
        # Heuristic function: Manhattan distance to the nearest treasure
        if not self.treasure_positions:
            return float('inf')
        return min(abs(position[0] - t[0]) + abs(position[1] - t[1]) for t in self.treasure_positions)

    def gbfs(self):
        # Greedy Best-First Search (GBFS) algorithm to find all treasures
        total_cost = 0
        treasures_to_find = len(self.treasure_positions)
        encountered_remove_treasures_trap = False

        # Priority queue (list) initialized with the entry point
        priority_queue = [(self.heuristic(self.entry), 0, self.entry, 1, 1)]
        local_visited = set()

        while self.collected_treasures < treasures_to_find and priority_queue:
            # Sort the priority queue based on the heuristic value
            priority_queue.sort(key=lambda x: x[0])
            _, cost, position, energy, steps = priority_queue.pop(0)
            print(f"Current state: cost={cost}, position={position}, energy={energy}, steps={steps}")

            if position in self.visited:
                # Skip positions that have already been visited
                print(f"Position {position} already visited.")
                continue

            self.visited.add(position)
            local_visited.add(position)

            if position in self.treasure_positions:
                # Collect treasure if the position contains a treasure
                total_cost += cost
                self.treasure_positions.remove(position)
                self.collected_treasures += 1
                self.entry = position
                print(f"Found treasure at position {position}. Total cost so far: {total_cost}")

            for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                # Explore adjacent positions
                new_r, new_c = position[0] + dr, position[1] + dc
                if self.in_bounds(new_r, new_c) and (new_r, new_c) not in local_visited:
                    new_position = (new_r, new_c)
                    new_position, new_energy, new_steps = self.apply_effects(new_position, energy, steps)
                    new_cost = cost + new_energy

                    # Add new position to the priority queue
                    priority_queue.append((self.heuristic(new_position), new_cost, new_position, new_energy, new_steps))

                    if new_position != position:
                        # Print applied effect information if the position changes due to an effect
                        print(f"Applied effect '{self.position_tracker[-1][1]}' at position {new_position}")

                    if self.grid[new_position[0]][new_position[1]] in self.traps:
                        # Check if the new position contains a trap that removes treasures
                        trap_effect = self.traps[self.grid[new_position[0]][new_position[1]]]
                        if trap_effect == 'remove_treasures':
                            print(f"Encountered trap '{self.grid[new_position[0]][new_position[1]]}' that removes treasures. Ending search.")
                            encountered_remove_treasures_trap = True
                            break

            if encountered_remove_treasures_trap:
                # End search if a trap that removes treasures is encountered
                print("Search ended due to encountering trap that removes treasures.")
                break

        return total_cost

    def print_grid(self):
        # Print the current state of the grid
        legend = {
            'Treasure': 'T',
            'Reward1': 'R1',
            'Reward2': 'R2',
            'Obstacle': 'X',
            'Empty': '-'
        }
        print("\nCurrent Grid State:")
        for row in self.grid:
            line = ' '.join([legend[cell] if cell in legend else cell for cell in row])
            print(line)

def randomize_grid(grid):
    # Randomize the grid, except for the initial spawn positions
    flat_grid = [item for row in grid for item in row]

    no_spawn_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

    items_to_randomize = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in no_spawn_positions:
                items_to_randomize.append(grid[r][c])

    random.shuffle(items_to_randomize)

    index = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) not in no_spawn_positions:
                grid[r][c] = items_to_randomize[index]
                index += 1

    return grid

# Initial grid setup
initial_grid = [
    ['Empty','Empty','Empty','Reward1','Empty','Empty','Empty', 'Empty','Empty','Empty'],
    ['Empty','Trap2','Empty','Trap4','Treasure','Empty','Trap3','Empty','Obstacle','Empty'],
    ['Empty','Empty','Obstacle','Empty','Obstacle','Empty','Empty','Reward2','Trap1','Empty'],
    ['Obstacle','Reward1','Empty','Obstacle','Empty','Trap3','Obstacle','Treasure','Empty','Treasure'],
    ['Empty','Empty','Trap2','Treasure','Obstacle','Empty','Obstacle','Obstacle','Empty','Empty'],
    ['Empty','Empty','Empty','Empty','Empty','Reward2','Empty','Empty','Empty','Empty']
]

# Define traps and their effects
traps = {
    'Trap1': 'increase_gravity',
    'Trap2': 'decrease_speed',
    'Trap3': 'move_two_cells',
    'Trap4': 'remove_treasures'
}

# Define rewards and their effects
rewards = {
    'Reward1': 'decrease_gravity',
    'Reward2': 'increase_speed'
}

# Entry point in the grid
entry = (0, 0)

# Randomize the grid
grid = randomize_grid(initial_grid)

# Create an instance of the VirtualWorld
virtual_world = VirtualWorld(grid, traps, rewards, entry)

# Print the initial grid state
virtual_world.print_grid()

# Run the greedy best-first search algorithm to find all treasures
total_cost = virtual_world.gbfs()

# Print the grid state after the search
print(f"\nTotal cost to find all treasures: {total_cost}")
