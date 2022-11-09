# KenKen Solver
## Background
Kenken is an arithmetic and logic puzzle, somewhat similar to Sudoku. It was created by Tetsuya Miyamoto, a Japanese math teacher, in 2004. A puzzle consists of an n /times n grid, typically ranging from 3 /times 3 to 9 /times 9. Just as in Sudoku, no number can be repeated in a row or column. Unlike the 3 /times 3 boxes in Sudoku, boxes in KenKen are of variable size and contain a target number as well as a mathematical operator. Applying the operator to the numbers in the box must yield the target.
/<Insert Example/>

### AC-3 Algorithm
The AC-3 algorithm is a constraint satisfaction algorithm developed by Alan Mackworth in 1977. It treats the current state as a directed graph, where nodes are the variables and edges (arcs) are the constraints between them. The algorithm systematically removes values from the domain of a variable if it is inconsistent with any of the node's constraints. The remaining values in a node's domain after running AC-3 are the possible values in a satisfying assignment. AC-3 is often used with backtrack search to solve puzzles such as Sudoku.
  
### Backtrack Search
Backtrack search is a form of depth-first traversal, which attempts to assign values to each node from its domain such that the entire assignment is consistent. Backtrack search simply chooses values from each nodes' domain until it encounters an assignment that violates some constraint. It then reverts to the last partial consistent assignment (backtracks) and continues. This process repeates until a satisfying assignment is found or it is determined that no satisfying assignment exists. Backtrack search is much more efficient than randomly tryiing assignments because any time it encounters an inconsistent assignment, it can prune the remainder of that path.
  
## Solving a KenKen
We will use AC-3 and backtrack search to solve KenKen puzzles. Representing the constraints of a KenKen puzzle is much more complex than representing those of a Sudoku since the constraints on the boxes are highly variable and depend on the values of differnt mathematical operations. We will essentially run two forms of the AC-3 algorithm to reduce the initial domains of our nodes and then check for both row/column consistency and box consistency while running backtrack search.

  ### Setting up the Domains and Constraints
Each box can have one of 4 operations: add, subtract, multiply, or divide. In some cases a box consists of a single square and the value is given. We take each box as input from the user in the format \<operator> </number of squares in the box> /<coordinate of box 1/> ... /<coordinate of box n/>. The following code initializes each node's domain to (1..n) unless the value is given (in which case we can already assign the value) and creates edges between nodes that share a row/column and nodes that belong to the same box:
```
def read_input():
  constraints = []
  size = int(sys.stdin.readline().strip())
  num_constraints = int(sys.stdin.readline().strip())
  for i in range(num_constraints):
      constraint = sys.stdin.readline().strip()
      constraint = constraint.split(' ')
      constraint[1] = int(constraint[1])
      for j in range(2, len(constraint)):
          constraint[j] = (int(constraint[j][0]), int(constraint[j][2]))
      constraints.append(constraint)
  return size, num_constraints, constraints
  
def createDomains(self):
    for i in range(self.size):
        for j in range(self.size):
            self.domains[(i,j)] = []
            for k in range(self.size):
                self.domains[(i,j)].append(k + 1)

"""
Creates arc between positions on same column or row
"""
def createArcs(self):
    for i in range(self.size):
        for j in range(self.size):
            self.arcs[(i,j)] = []
    for arc in self.arcs:
        for i in range(self.size):
            if i != arc[1]:
                self.arcs[arc].append((arc[0], i))
        for i in range(self.size):
            if i != arc[0]:
                self.arcs[arc].append((i, arc[1]))
    
"""
Adds constraint for each position based on arithmetic box it is a member of
"""
def addConstraints(self, constraints):
  for i in range(len(constraints)):
        if constraints[i][0] != 'v':
            for j in range(2, len(constraints[i])):
                self.constraints[constraints[i][j]] = []
                for k in range(len(constraints[i])):
                    if constraints[i][k] != constraints[i][j]:
                        self.constraints[constraints[i][j]].append(constraints[i][k])
```

### Dual AC-3
