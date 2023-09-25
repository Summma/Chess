# Chess

## Description
This chess engine implements the minimax algorithm to recursively iterate through the set of all possible moves at each position. The score of each position is determined by a hand crafted 
set of parameters that I found using the chess wiki: https://www.chessprogramming.org/Main_Page <br/>
To summarize, this includes:
- Transposition Tables
- Zobrist Hashing
- Alpha-Beta Pruning
- Quiesence Search
- Iterative Deepening
- Piece Ordering
- Piece-Value Tables
- ... etc

Some of these techniques are not exclusive to the game of chess, and can be applied to other games where moves can be represented by a tree if the technique is broadened.

## How to run
Run the chess engine by running the Board.py file, and this allows you to play against the engine with the white pieces. The side should contain some information about how the engine evaluates the
current board, the depth it went to, and other pieces of important information.
