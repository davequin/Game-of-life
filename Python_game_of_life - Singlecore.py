# Import modules
import random, numpy
from tqdm import tqdm
from PIL import Image
from time import sleep

# Define the size of the grid
x_axis = 10
y_axis = 10

# number of squares to randomly select
starting_cells = 50

# creating the array to hold the game board
print(f"Creating the Game board...")
board = numpy.zeros((x_axis, y_axis), dtype=numpy.uint8)

# list holding all of the random starting postions
starting_positions = []

# percentage chance for a block to be flipped to on (Lower means further spread apart)
chance = 5

# name of gif file we want to save the board to
GIF_name = "Game of Life.gif"

# setting the resolution for the final gif file
x_resolution = 1920
y_resolution = 1080

# setting a maximum number of iterations to loop for in case the board stays alive indefintely
MAX_ITERATIONS = 100

# rules for conways game of life
# 1. if a cell has less than 2 live neighbors it dies
# 2. if a cell has more than 3 live neighbors it dies 
# 3. if a cell has exactly 3 live neighbors an isn't alive already it becomes alive
# 4. if a cell has 2 or 3 neighbors it stays alive

# function to compute the next time step
def compute_next_time_step(board, toroidal = False):
    x_limit, y_limit = board.shape
    changes = {}
    number_of_changes = 0
    at_least_1_live_cell = False
    for position, alive in numpy.ndenumerate(board):
        live_neighbors = 0
        if alive:
            at_least_1_live_cell = True
        if toroidal:
            # up
            if board[position[0], (position[1] - 1) % y_limit]:
                live_neighbors += 1
            # down
            if board[position[0], (position[1] + 1) % y_limit]:
                live_neighbors += 1
            # left
            if board[(position[0] - 1) % x_limit, position[1]]:
                live_neighbors += 1
            # right
            if board[(position[0] + 1) % x_limit, position[1]]:
                live_neighbors += 1
            # top left
            if board[(position[0] - 1) % x_limit, (position[1] - 1) % y_limit]:
                live_neighbors += 1
            # top right
            if board[(position[0] + 1) % x_limit, (position[1] - 1) % y_limit]:
                live_neighbors += 1
            # bottom left
            if board[(position[0] - 1) % x_limit, (position[1] + 1) % y_limit]:
                live_neighbors += 1
            # bottom right
            if board[(position[0] + 1) % x_limit, (position[1] + 1) % y_limit]:
                live_neighbors += 1
        else:
            # up
            if position[1] > 0:
                if board[position[0], position[1] - 1]:
                    live_neighbors += 1
            # down
            if position[1] < y_limit:
                if board[position[0], position[1] + 1]:
                    live_neighbors += 1
            # left
            if position[0] > 0:
                if board[position[0] - 1, position[1]]:
                    live_neighbors += 1
            # right
            if position[0] < x_limit:
                if board[position[0] + 1, position[1]]:
                    live_neighbors += 1
            # top left
            if not (position[0] == 0) and not (position[1] == 0):
                if board[position[0] - 1, position[1] - 1]:
                    live_neighbors += 1
            # top right
            if not (position[0] == x_limit - 1) and not (position[1] == 0):
                if board[position[0] + 1, position[1] - 1]:
                    live_neighbors += 1
            # bottom left
            if not (position[0] == 0) and not (position[1] == y_limit - 1):
                if board[position[0] - 1, position[1] + 1]:
                    live_neighbors += 1
            # bottom right
            if not (position[0] == x_limit - 1) and not (position[1] == y_limit - 1):
                if board[position[0] + 1, position[1] + 1]:
                    live_neighbors += 1

        if board[position]:
            # rule 1 underpopulation
            if live_neighbors < 2:
                changes[number_of_changes] = position
                number_of_changes += 1
            # rule 2 overpopulation
            elif live_neighbors > 3:
                changes[number_of_changes] = position
                number_of_changes += 1
        # rule 3 reproduction
        elif live_neighbors == 3:
            changes[number_of_changes] = position
            number_of_changes += 1
        # rule 4 surviaval

    if not at_least_1_live_cell:
        return(False)

    for key in changes.keys():
        board[changes[key]] = ~board[changes[key]]
    return(board)

# checking to make sure only a valid number of blocks can be flipped before moving into the while loop
if starting_cells > x_axis * y_axis:
    raise ValueError(f"Selected {starting_cells} starting positions to be set to true when only {x_axis * y_axis} exist.")

# checking to make sure the board is not all zeros
if chance <= 0:
    if not starting_cells == 0:
        raise ValueError("Percentage chance must be set greater than 0 or the number of starting cells must be 0.")

# setting the board's starting 
bar = tqdm(total = starting_cells, desc = "Setting starting state")
while starting_cells > 0:
    # looping through the entire board
    for flip, value in numpy.ndenumerate(board):
        # checking to see if enough cells have been set to alive
        if starting_cells <= 0:
            # exiting the loop
            break
        # rolling the dice to see if the current cell should be set to alive
        number = random.randint(1, 101)
        # checking if the current cell should be set to alive
        if number <= chance:
            # making sure the cell isn't already alive
            if not value:
                # setting the current cell to alive
                board[*flip] = ~(board[*flip])
                # decrementing the number of cells that need to be set to alive
                starting_cells -= 1
                bar.update(1)
bar.close()

iterations = 0
all_frames = {}
bar = tqdm(total=MAX_ITERATIONS, desc = "Calculating the board state")
while type(board) != bool and iterations < MAX_ITERATIONS:
    image = Image.fromarray(board, mode = "L") # 'L' = grayscale
    image = image.resize((x_resolution, y_resolution), Image.NEAREST)
    all_frames[iterations] = image
    board = compute_next_time_step(board, toroidal = True)
    iterations += 1
    bar.update(1)
bar.close()

# Saveing as a GIF
print(f"Saving as GIF to : {GIF_name}")
all_frames = list(all_frames.values())
all_frames[0].save(
    GIF_name,
    save_all=True,
    append_images=all_frames[1:],
    duration=150,   # milliseconds per frame
    loop=0          # infinite loop
)















