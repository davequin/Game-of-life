# Import modules
from multiprocessing import shared_memory, Process, Barrier, Event
import numpy

def worker(shared_buffer_name, shape, dtype, chunk, if_toroidal, sync_barrier,  kill_signal):

# rules for conways game of life
# 1. if a cell has less than 2 live neighbors it dies
# 2. if a cell has more than 3 live neighbors it dies 
# 3. if a cell has exactly 3 live neighbors an isn't alive already it becomes alive
# 4. if a cell has 2 or 3 neighbors it stays alive

    def read_chunks(shape, start, index=(), is_first=True):
            if len(index) == len(shape):
                yield index
            else:
                dim = len(index)
                start_i = start[dim] if is_first else 0
                for i in range(start_i, shape[dim]):
                    yield from read_chunks(shape, start, index + (i,), is_first and i == start_i)
        
    # Attach to the shared memory block
    shared_buffer = shared_memory.SharedMemory(name=shared_buffer_name)
    shared_array = numpy.ndarray(shape, dtype=dtype, buffer=shared_buffer.buf)
    x_limit, y_limit = shared_array.shape
    while not kill_signal.is_set():
        changes = {}
        number_of_changes = 0
        sync_barrier.wait()
        if type(chunk[0]) == tuple:
            for position in read_chunks(shape, chunk[0]):
                if position == chunk[1]:
                    break
                live_neighbors = 0
                if if_toroidal:
                    # up
                    if shared_array[position[0], (position[1] - 1) % y_limit]:
                        live_neighbors += 1
                    # down
                    if shared_array[position[0], (position[1] + 1) % y_limit]:
                        live_neighbors += 1
                    # left
                    if shared_array[(position[0] - 1) % x_limit, position[1]]:
                        live_neighbors += 1
                    # right
                    if shared_array[(position[0] + 1) % x_limit, position[1]]:
                        live_neighbors += 1
                    # top left
                    if shared_array[(position[0] - 1) % x_limit, (position[1] - 1) % y_limit]:
                        live_neighbors += 1
                    # top right
                    if shared_array[(position[0] + 1) % x_limit, (position[1] - 1) % y_limit]:
                        live_neighbors += 1
                    # bottom left
                    if shared_array[(position[0] - 1) % x_limit, (position[1] + 1) % y_limit]:
                        live_neighbors += 1
                    # bottom right
                    if shared_array[(position[0] + 1) % x_limit, (position[1] + 1) % y_limit]:
                        live_neighbors += 1
                else:
                    # up
                    if position[1] > 0:
                        if shared_array[position[0], position[1] - 1]:
                            live_neighbors += 1
                    # down
                    if position[1] < y_limit:
                        if shared_array[position[0], position[1] + 1]:
                            live_neighbors += 1
                    # left
                    if position[0] > 0:
                        if shared_array[position[0] - 1, position[1]]:
                            live_neighbors += 1
                    # right
                    if position[0] < x_limit:
                        if shared_array[position[0] + 1, position[1]]:
                            live_neighbors += 1
                    # top left
                    if not (position[0] == 0) and not (position[1] == 0):
                        if shared_array[position[0] - 1, position[1] - 1]:
                            live_neighbors += 1
                    # top right
                    if not (position[0] == x_limit - 1) and not (position[1] == 0):
                        if shared_array[position[0] + 1, position[1] - 1]:
                            live_neighbors += 1
                    # bottom left
                    if not (position[0] == 0) and not (position[1] == y_limit - 1):
                        if shared_array[position[0] - 1, position[1] + 1]:
                            live_neighbors += 1
                    # bottom right
                    if not (position[0] == x_limit - 1) and not (position[1] == y_limit - 1):
                        if shared_array[position[0] + 1, position[1] + 1]:
                            live_neighbors += 1

                if shared_array[position]:
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

        else:
            position = chunk
            live_neighbors = 0
            if if_toroidal:
                # up
                if shared_array[position[0], (position[1] - 1) % y_limit]:
                    live_neighbors += 1
                # down
                if shared_array[position[0], (position[1] + 1) % y_limit]:
                    live_neighbors += 1
                # left
                if shared_array[(position[0] - 1) % x_limit, position[1]]:
                    live_neighbors += 1
                # right
                if shared_array[(position[0] + 1) % x_limit, position[1]]:
                    live_neighbors += 1
                # top left
                if shared_array[(position[0] - 1) % x_limit, (position[1] - 1) % y_limit]:
                    live_neighbors += 1
                # top right
                if shared_array[(position[0] + 1) % x_limit, (position[1] - 1) % y_limit]:
                    live_neighbors += 1
                # bottom left
                if shared_array[(position[0] - 1) % x_limit, (position[1] + 1) % y_limit]:
                    live_neighbors += 1
                # bottom right
                if shared_array[(position[0] + 1) % x_limit, (position[1] + 1) % y_limit]:
                    live_neighbors += 1
            else:
                # up
                if position[1] > 0:
                    if shared_array[position[0], position[1] - 1]:
                        live_neighbors += 1
                # down
                if position[1] < y_limit:
                    if shared_array[position[0], position[1] + 1]:
                        live_neighbors += 1
                # left
                if position[0] > 0:
                    if shared_array[position[0] - 1, position[1]]:
                        live_neighbors += 1
                # right
                if position[0] < x_limit:
                    if shared_array[position[0] + 1, position[1]]:
                        live_neighbors += 1
                # top left
                if not (position[0] == 0) and not (position[1] == 0):
                    if shared_array[position[0] - 1, position[1] - 1]:
                        live_neighbors += 1
                # top right
                if not (position[0] == x_limit - 1) and not (position[1] == 0):
                    if shared_array[position[0] + 1, position[1] - 1]:
                        live_neighbors += 1
                # bottom left
                if not (position[0] == 0) and not (position[1] == y_limit - 1):
                    if shared_array[position[0] - 1, position[1] + 1]:
                        live_neighbors += 1
                # bottom right
                if not (position[0] == x_limit - 1) and not (position[1] == y_limit - 1):
                    if shared_array[position[0] + 1, position[1] + 1]:
                        live_neighbors += 1

            if shared_array[position]:
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
        sync_barrier.wait()
        for position in changes.values():
            shared_array[position] = ~shared_array[position]

    shared_buffer.close()



if __name__ == "__main__":
    from tqdm import tqdm
    from PIL import Image
    from time import sleep
    import random

    def create_chunks(shape, number_of_processes):
        total = 1
        for demension in shape:
            total *= demension
        chunk_size = total // number_of_processes
        extra = total % number_of_processes
        all_chunks = {}
        chunks = []
        process = 1
        if extra == 0 and chunk_size == 1:
            for index in numpy.ndindex(shape):
                all_chunks[process] = (index)
                process += 1
            return all_chunks
        for index in numpy.ndindex(shape):
            if len(chunks) < chunk_size:
                chunks.append(index)
            elif extra > 0:
                chunks.append(index)
                all_chunks[process] = (chunks[0], chunks[-1])
                process += 1
                extra -= 1
                chunks = []
            elif len(chunks) == chunk_size:
                all_chunks[process] = (chunks[0], chunks[-1])
                process += 1
                chunks = []
                chunks.append(index)
        all_chunks[process] = (chunks[0], chunks[-1])
        for index, chunks in all_chunks.items():
            if len(chunks) == 2:
                if chunks[0] == chunks[-1]:
                    all_chunks[index] = (chunks[0])
        return all_chunks

    # Define the size of the grid
    x_axis = 1000
    y_axis = 1000

    # number of squares to randomly select
    starting_cells = 550000

    # setting a maximum number of iterations to loop for in case the board stays alive indefintely
    MAX_ITERATIONS = 5000

    # setting the number of processes to create to accelerate rendering the game board
    number_of_processes = 32

    # setting wether or not to treat the game board as toroidal (roll over back to the begining)
    if_toroidal = True

    # percentage chance for a block to be flipped to on (Lower means further spread apart)
    chance = 5

    # name of gif file we want to save the board to
    GIF_NAME = "Game of Life.gif"

    # setting the resolution for the final gif file
    x_resolution = 1920
    y_resolution = 1080

    # creating the array to hold the game board
    print(f"Creating the Game board...")
    board = numpy.zeros((x_axis, y_axis), dtype=numpy.uint8)
    shared_buffer = shared_memory.SharedMemory(create=True, size=board.nbytes)
    shared_array = numpy.ndarray(board.shape, dtype=board.dtype, buffer=shared_buffer.buf)
    shared_array[:] = board[:]
    # deleting the old board to free up space
    del board

    # list holding all of the random starting postions
    starting_positions = []

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
        for flip, value in numpy.ndenumerate(shared_array):
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
                    shared_array[*flip] = ~(shared_array[*flip])
                    # decrementing the number of cells that need to be set to alive
                    starting_cells -= 1
                    bar.update(1)
    bar.close()


    chunks = create_chunks(shared_array.shape, number_of_processes)
    barrier = Barrier(number_of_processes + 1)
    kill_signal = Event()
    workers = {}
    for x in range(1, number_of_processes + 1):
        workers[x] = Process(target=worker, args=(shared_buffer.name, shared_array.shape, shared_array.dtype, chunks[x], if_toroidal, barrier,  kill_signal))
        workers[x].start()

    iterations = 0
    all_frames = [0] * MAX_ITERATIONS
    bar = tqdm(total=MAX_ITERATIONS, desc = "Calculating the board state")
    while iterations < MAX_ITERATIONS:
        # read the array
        barrier.wait()
        image = Image.fromarray(shared_array, mode = "L") # 'L' = grayscale
        image = image.resize((x_resolution, y_resolution), Image.NEAREST)
        all_frames[iterations] = image
        if iterations == MAX_ITERATIONS - 1:
            kill_signal.set()
        # update the array
        barrier.wait()
        iterations += 1
        bar.update(1)
    bar.close()

    # Saveing as a GIF
    print(f"Saving as GIF to : {GIF_NAME}")
    all_frames[0].save(
        GIF_NAME,
        save_all=True,
        append_images=all_frames[1:],
        duration=150,   # milliseconds per frame
        loop=0          # infinite loop
    )