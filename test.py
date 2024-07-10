import random

class VirtualWorld:
    def __init__(self, grid, traps, rewards, entry):
        self.grid = grid
        self.traps = traps
        self.rewards = rewards
        self.entry = entry
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.treasure_positions = self.get_positions('Treasure')
        self.visited = set()
        self.collected_treasures = 0
        self.max_iterations = 10000  # Prevent infinite loops

    def get_positions(self, item_type):
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == item_type:
                    positions.append((r, c))
        return positions

    def count_elements(self):
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
        return 0 <= r < self.rows and 0 <= c < self.cols

    def apply_effects(self, position, energy, steps, last_move):
        cell = self.grid[position[0]][position[1]]
        if cell in self.traps:
            effect = self.traps[cell]
            print(f"Encountered {cell} at position {position}. Effect: {effect}")
            if effect == 'increase_gravity':
                energy *= 2
            elif effect == 'decrease_speed':
                steps *= 2
            elif effect == 'move_two_cells':
                new_r = position[0] + 2 * last_move[0]
                new_c = position[1] + 2 * last_move[1]
                if self.in_bounds(new_r, new_c):
                    position = (new_r, new_c)
                else:
                    position = (new_r - last_move[0], new_c - last_move[1])  # Move one cell back if out of bounds
            elif effect == 'remove_treasures':
                self.treasure_positions = []
        elif cell in self.rewards:
            effect = self.rewards[cell]
            print(f"Encountered {cell} at position {position}. Effect: {effect}")
            if effect == 'decrease_gravity':
                energy = max(1, energy // 2)  # Prevent energy from becoming zero
            elif effect == 'increase_speed':
                steps = max(1, steps // 2)  # Prevent steps from becoming zero
        return position, energy, steps

    def gbfs(self):
        total_cost = 0
        treasures_to_find = len(self.treasure_positions)
        iteration = 0

        while self.collected_treasures < treasures_to_find and iteration < self.max_iterations:
            queue = [(0, self.entry, 1, 1)]  # (cost, position, energy, steps)
            self.visited = set()

            while queue and self.collected_treasures < treasures_to_find:
                iteration += 1
                if iteration >= self.max_iterations:
                    print("Reached maximum iteration limit, stopping search.")
                    break

                # Shuffle the directions for random exploration
                directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                random.shuffle(directions)

                # Pop the first element (lowest cost) from the queue
                cost, position, energy, steps = queue.pop(0)

                if position in self.treasure_positions:
                    total_cost += cost
                    self.treasure_positions.remove(position)
                    self.collected_treasures += 1
                    self.entry = position  # Start next search from the current treasure position
                    print(f"Found treasure at position {position}. Total cost so far: {total_cost}")

                self.visited.add(position)
                for dr, dc in directions:
                    new_r, new_c = position[0] + dr, position[1] + dc
                    new_position = (new_r, new_c)
                    if self.in_bounds(new_r, new_c) and new_position not in self.visited:
                        self.visited.add(new_position)
                        new_position, new_energy, new_steps = self.apply_effects(new_position, energy, steps, (dr, dc))
                        new_cost = cost + new_energy
                        # Insert the new state into the queue maintaining sorted order
                        self.insert_sorted(queue, (new_cost, new_position, new_energy, new_steps))

        if self.collected_treasures < treasures_to_find:
            print("Could not find all treasures within iteration limit.")

        return total_cost

    def insert_sorted(self, queue, item):
        """
        Insert an item into the queue maintaining sorted order.

        :param queue: The priority queue list.
        :param item: The item to insert.
        """
        for i in range(len(queue)):
            if item[0] < queue[i][0]:
                queue.insert(i, item)
                return
        queue.append(item)

    def print_grid(self):
        """
        Print the current state of the grid with a legend for symbols.
        """
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
    flat_grid = [item for row in grid for item in row]
    random.shuffle(flat_grid)  # Shuffle the grid elements randomly
    randomized_grid = [flat_grid[i:i + len(grid[0])] for i in range(0, len(flat_grid), len(grid[0]))]
    return randomized_grid

# Define the initial grid and effects
initial_grid = [
    ['Empty', 'Empty', 'Trap1', 'Empty', 'Reward1', 'Empty', 'Trap2', 'Empty'],
    ['Empty', 'Obstacle', 'Empty', 'Empty', 'Empty', 'Obstacle', 'Empty', 'Trap3'],
    ['Reward2', 'Empty', 'Empty', 'Obstacle', 'Empty', 'Trap4', 'Empty', 'Treasure'],
    ['Empty', 'Empty', 'Empty', 'Empty', 'Obstacle', 'Empty', 'Empty', 'Empty']
]

traps = {
    'Trap1': 'increase_gravity',
    'Trap2': 'decrease_speed',
    'Trap3': 'move_two_cells',
    'Trap4': 'remove_treasures'
}

rewards = {
    'Reward1': 'decrease_gravity',
    'Reward2': 'increase_speed'
}

entry = (0, 0)

# Randomize the grid and find all treasures and rewards
grid = randomize_grid(initial_grid)
virtual_world = VirtualWorld(grid, traps, rewards, entry)

# Print initial grid state
virtual_world.print_grid()

# Run the GBFS algorithm
total_cost = virtual_world.gbfs()

# Print final grid state
virtual_world.print_grid()

print(f"\nTotal cost to find all treasures: {total_cost}")

