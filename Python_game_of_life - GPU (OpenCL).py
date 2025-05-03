import random, numpy, pyopencl
from tqdm import tqdm
from PIL import Image
from time import sleep

# Define the size of the grid
x_axis = 1000
y_axis = 1000

# number of squares to randomly select
starting_cells = 550000

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
MAX_ITERATIONS = 20000

# rules for conways game of life
# 1. if a cell has less than 2 live neighbors it dies
# 2. if a cell has more than 3 live neighbors it dies 
# 3. if a cell has exactly 3 live neighbors an isn't alive already it becomes alive
# 4. if a cell has 2 or 3 neighbors it stays alive

# checking to make sure only a valid number of blocks can be flipped before moving into the while loop
if starting_cells > x_axis * y_axis:
    raise ValueError(f"Selected {starting_cells} starting positions to be set to true when only {x_axis * y_axis} exist.")

# checking to make sure the board is not all zeros
if chance <= 0:
    if not starting_cells == 0:
        raise ValueError("Percentage chance must be set greater than 0 or the number of starting cells must be 0.")

# setting the board's starting state
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

# selecting which device to run on
device_selection = 0

# setting up opencl
platform = pyopencl.get_platforms()[0]
device = platform.get_devices()
if len(device) > 1:
    context = pyopencl.Context([device[device_selection % len(device)]])
    queue = pyopencl.CommandQueue(context)
else:
    context = pyopencl.Context([device[0]])
    queue = pyopencl.CommandQueue(context)

# creating buffers to hold the game state
memory_flags = pyopencl.mem_flags
first_gpu_copy = pyopencl.Buffer(context, memory_flags.READ_WRITE, board.nbytes)
second_gpu_copy = pyopencl.Buffer(context, memory_flags.READ_WRITE, board.nbytes)

# getting gpu code
kernel_code = """
__kernel void compute_next_time_step(__global unsigned char* game_board, __global unsigned char* change_board, const unsigned int width, const unsigned int height, const char toriodal) {
    int y = get_global_id(0);
    int x = get_global_id(1);

    char live_neighbors = 0;

    if (toriodal) {
        // Left
        if (game_board[y * width + ((x -1) % width)]) {
            live_neighbors += 1;
        }
        //right
        if (game_board[y * width + ((x + 1) % width)]) {
            live_neighbors += 1;
        }
        //up
        if (game_board[((y - 1) % height) * width + x]) {
            live_neighbors += 1;
        }
        //down
        if (game_board[((y + 1) % height) * width + x]) {
            live_neighbors += 1;
        }
        //top left
        if (game_board[((y - 1) % height) * width + ((x - 1) % width)]) {
            live_neighbors += 1;
        }
        //top right
        if (game_board[((y - 1) % height) * width + ((x + 1) % width)]) {
            live_neighbors += 1;
        }
        //bottom left
        if (game_board[((y + 1) % height) * width + ((x - 1) % width)]) {
            live_neighbors += 1;
        }
        //bottom right
        if (game_board[((y + 1) % height) * width + ((x + 1) % width)]) {
            live_neighbors += 1;
        }

    }
    else {
        // Left
        if (x == 0) {
            // automaticly not alive
        }
        else {
            if (game_board[y * width + (x - 1)]) {
                live_neighbors += 1;
            }
        }
        //right
        if (x == (width - 1)) {
            // automaticly not alive
        }
        else {
            if (game_board[y * width + (x + 1)]) {
                live_neighbors += 1;
            }
        }
        //up
        if (y == 0) {
            // automaticly not alive
        }
        else {
            if (game_board[(y - 1) * width + x]) {
                live_neighbors += 1;
            }
        }
        //down
        if (y == (height - 1)) {
            // automaticly not alive
        }
        else {
            if (game_board[(y + 1) * width + x]) {
                live_neighbors += 1;
            }
        }
        //top left
        if (x != 0 && y != 0) {
            if (game_board[(y - 1) * width + (x - 1)]) {
                live_neighbors += 1;
            }
        }
        //top right
        if (x != (width - 1) && y != 0) {
            if (game_board[(y - 1) * width + (x + 1)]) {
                live_neighbors += 1;
            }
        }
        //bottom left
        if (x != 0 && y != (height - 1)) {
            if (game_board[(y + 1) * width + (x - 1)]) {
                live_neighbors += 1;
            }
        }
        //bottom right
        if (x != (width - 1) && y != (height - 1)) {
            if (game_board[(y + 1) * width + (x + 1)]) {
                live_neighbors += 1;
            }
        }
    }

    // rules for conways game of life
    // 1. if a cell has less than 2 live neighbors it dies
    // 2. if a cell has more than 3 live neighbors it dies 
    // 3. if a cell has exactly 3 live neighbors an isn't alive already it becomes alive
    // 4. if a cell has 2 or 3 neighbors it stays alive
    // if alive
    if (game_board[y * width + x]) {
        // rule 1
        if (live_neighbors < 2) {
            //flip
            change_board[y * width + x] = ~game_board[y * width + x];
        // rule 2
        }else if (live_neighbors > 3) {
            // flip
            change_board[y * width + x] = ~game_board[y * width + x];
        }else {
            change_board[y * width + x] = game_board[y * width + x];
        }

    }
    else
    {   //rule 3
        if (live_neighbors == 3) {
        //flip
            change_board[y * width + x] = ~game_board[y * width + x];
        }else {
            change_board[y * width + x] = game_board[y * width + x];
        }
    }
}
"""

# compile the kernel
program = pyopencl.Program(context, kernel_code).build()

# setup kernel arguments
width = board.shape[1]  # Number of columns (width of the 2D array)
height = board.shape[0]  # Number of rows (height of the 2D array)
toriodal = True
kernel = program.compute_next_time_step
kernel.set_arg(2, numpy.uint32(width))  # Pass the width of the array
kernel.set_arg(3, numpy.uint32(height))  # Pass the height of the array
kernel.set_arg(4, numpy.uint8(toriodal)) # Pass the boolean

# copy array to the gpu
pyopencl.enqueue_copy(queue, first_gpu_copy, board).wait()
pyopencl.enqueue_copy(queue, second_gpu_copy, board).wait()

# Step 7: Define the global and local work sizes
global_size = board.shape  # Global work size corresponds to the array shape (rows, cols)
local_size = (1, 1)  # A work group of 1x1 (optional optimization)

iterations = 0
all_frames = {}
# copy frame 0 the start of the board
image = Image.fromarray(board, mode = "L") # 'L' = grayscale
image = image.resize((x_resolution, y_resolution), Image.NEAREST)
all_frames[iterations] = image
bar = tqdm(total=MAX_ITERATIONS, desc = "Calculating the board state")
while iterations < MAX_ITERATIONS:
    if not iterations % 2:
        kernel.set_arg(0, first_gpu_copy)  # Pass the OpenCL buffer
        kernel.set_arg(1, second_gpu_copy)  # Pass the second buffer
    else:
        # flip the buffers
        kernel.set_arg(0, second_gpu_copy)  # Pass the OpenCL buffer
        kernel.set_arg(1, first_gpu_copy)  # Pass the second buffer
    # Execute the kernel
    pyopencl.enqueue_nd_range_kernel(queue, kernel, global_size, local_size).wait()
    #queue.finish()
    # Retrieve the data from the device
    if not iterations % 2:
        pyopencl.enqueue_copy(queue, board, second_gpu_copy).wait()
    else:
        pyopencl.enqueue_copy(queue, board, first_gpu_copy).wait()
    #queue.finish()

    # convert the result to an image
    image = Image.fromarray(board, mode = "L") # 'L' = grayscale
    # resize the image for viewing
    image = image.resize((x_resolution, y_resolution), Image.NEAREST)
    # store the image
    all_frames[iterations] = image
    # increment the number of iterations
    iterations += 1
    # update the progress bar
    bar.update(1)
bar.close()

# Saving as a GIF
print(f"\nSaving as GIF to : {GIF_name}")
all_frames = list(all_frames.values())
all_frames[0].save(
    GIF_name,
    save_all=True,
    append_images=all_frames[1:],
    duration=1,   # milliseconds per frame
    loop=1          # 0 means infinite loop
)