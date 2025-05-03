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