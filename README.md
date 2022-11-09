# KenKen Solver
### Overview
Kenken is an arithmetic and logic puzzle, somewhat similar to Sudoku. It was created by Tetsuya Miyamoto, a Japanese math teacher, in 2004. A puzzle consists of an n /times n grid, typically ranging from 3 /times 3 to 9 /times 9. Just as in Sudoku, no number can be repeated in a row or column. Unlike the 3 /times 3 boxes in Sudoku, boxes in KenKen are of variable size and contain a target number as well as a mathematical operator. Applying the operator to the numbers in the box must yield the target.
<Insert Example>

### AC-3 Algorithm
The AC-3 algorithm is a constraint satisfaction algorithm developed by Alan Mackworth in 1977. It treats the current state as a directed graph, where nodes are the variables and edges (arcs) are the constraints between them. The algorithm systematically removes values from the domain of a variable if the value is inconsistent with any of its constraints. The remaining values in a node's domain after running AC-3 are the possible values in a satisfying assignment. AC-3 is often used with backtrack search to solve puzzles such as Sudoku.
  
### Backtrack Search
Backtrack search is a form of depth-first traversal, which attempts to assign values to each node from its domain such that the entire assignment is consistent. Backtrack search simply chooses values from each nodes' domain until it encounters an assignment that violates some constraint. It then reverts to the last partial consistent assignment (backtracks) and continues. This process repeates until a satisfying assignment is found or it is determined that no satisfying assignment exists. Backtrack search is much more efficient than randomly tryiing assignments because any time it encounters an inconsistent assignment, it can prune the remainder of that path.
  
### Solving a KenKen
