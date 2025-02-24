import pygame
import serial
import time

# Initialize Bluetooth connection with HC-06
try:
    bluetooth = serial.Serial("/dev/rfcomm0", 9600, timeout=1)  # Adjust if needed
    print("Connected to HC-06")
    time.sleep(2)  # Allow time for connection
except Exception as e:
    print("Error connecting to Bluetooth:", e)
    exit()

# Maze Configuration (1 = Wall, 0 = Free Path)
maze = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

start = (4, 1)  # Robot start position
goal = (7, 5)   # Target position

# Possible movements: Right, Down, Left, Up
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
direction_names = ["right", "down", "left", "up"]

# BFS Algorithm to Solve Maze
def bfs(maze, start, goal):
    queue = [(start, [])]
    visited = set()
    
    while queue:
        (x, y), path = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if (x, y) == goal:
            return path  # Return shortest path

        for i, (dx, dy) in enumerate(directions):
            nx, ny = x + dx, y + dy
            if maze[nx][ny] == 0 and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [direction_names[i]]))

    return []

# Convert BFS Path to Real-World Movements
def convert_to_real_moves(bfs_path):
    direction = "right"  # Robot starts facing up
    movements = []

    for move in bfs_path:
        if move == "right":
            if direction == "up":
                movements.append("turn_right")
                movements.append("forward")
                direction = "right"
            elif direction == "right":
                movements.append("forward")
            elif direction == "down":
                movements.append("turn_left")
                movements.append("forward")
                direction = "right"
            elif direction == "left":
                movements.append("turn_right")
                movements.append("turn_right")
                movements.append("forward")
                direction = "right"

        elif move == "left":
            if direction == "up":
                movements.append("turn_left")
                movements.append("forward")
                direction = "left"
            elif direction == "right":
                movements.append("turn_left")
                movements.append("turn_left")
                movements.append("forward")
                direction = "left"
            elif direction == "down":
                movements.append("turn_right")
                movements.append("forward")
                direction = "left"
            elif direction == "left":
                movements.append("forward")

        elif move == "up":
            if direction == "up":
                movements.append("forward")
            elif direction == "right":
                movements.append("turn_left")
                movements.append("forward")
                direction = "up"
            elif direction == "down":
                movements.append("turn_right")
                movements.append("turn_right")
                movements.append("forward")
                direction = "up"
            elif direction == "left":
                movements.append("turn_right")
                movements.append("forward")
                direction = "up"

        elif move == "down":
            if direction == "up":
                movements.append("turn_right")
                movements.append("turn_right")
                movements.append("forward")
                direction = "down"
            elif direction == "right":
                movements.append("turn_right")
                movements.append("forward")
                direction = "down"
            elif direction == "down":
                movements.append("forward")
            elif direction == "left":
                movements.append("turn_left")
                movements.append("forward")
                direction = "down"

    return movements

# Send Movements to Arduino via Bluetooth
def send_movements_to_arduino(movements):
    for move in movements:
        print("Sending:", move)
        bluetooth.write((move + "\n").encode())  # Send command
        time.sleep(1)  # Wait for execution

# Maze Visualization with Pygame
def visualize_maze(maze, path):
    pygame.init()
    width, height = 500, 500
    cell_size = width // len(maze)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze Visualization")

    running = True
    clock = pygame.time.Clock()
    path_index = 0
    pos = start

    while running:
        screen.fill((255, 255, 255))

        # Draw Maze
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                color = (0, 0, 0) if maze[i][j] == 1 else (200, 200, 200)
                pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))

        # Draw Robot
        pygame.draw.circle(screen, (255, 0, 0), (pos[1] * cell_size + cell_size // 2, pos[0] * cell_size + cell_size // 2), cell_size // 3)

        pygame.display.flip()
        clock.tick(1)  # Delay for visualization

        if path_index < len(path):
            move = path[path_index]
            dx, dy = directions[direction_names.index(move)]
            pos = (pos[0] + dx, pos[1] + dy)
            path_index += 1
        else:
            running = False

    pygame.quit()

# Run Everything
bfs_path = bfs(maze, start, goal)
print("BFS Path:", bfs_path)

if bfs_path:
    
    movements = convert_to_real_moves(bfs_path)
    print("Converted Movements:", movements)
    send_movements_to_arduino(movements)
    
else:
    print("No path found!")
