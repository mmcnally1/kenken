# KenKen Solver
My dad introduced me to KenKens a while back, and while they can make for a fun challenge, they can also be quite difficult to solve. He occasionally sends me puzzles that he is stuck on and in the spirit of a true programmer, instead of taking a few minutes to try to solve them myself I decided to spend much longer writing a program to do it for me!
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
Each box can have one of 4 operations: add, subtract, multiply, or divide. In some cases a box consists of a single square and the value is given. We take each box as input from the user in the format \<operator> \<number of squares in the box> \<coordinate of box 1> ... \<coordinate of box n>. The following code initializes each node's domain to (1..n) unless the value is given (in which case we can already assign the value) and creates edges between nodes that share a row/column and nodes that belong to the same box:
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
Normally the AC-3 algorithm maintains a queue of arcs and removes values from the domain of the nodes associated with the arcs when they are in conflict. If the domain of a node is altered, each arc it belongs to is added to the queue and evaluated again. Since we have two types of constraints, we alternate between evaluating row/column arcs and box arcs. The following code demonstrates this.
```
"""
remove illegal values from each square's domain based on row/column constraints
"""
def AC3(self):
    revised = False
    q = deque()
    for arc in self.arcs:
        for var in self.arcs[arc]:
            q.append((arc, var))
    while q:
        (Xi, Xj) = q.popleft()
        if self.revise(Xi, Xj):
            assert len(self.domains[Xi]) > 0
            for Xk in self.arcs[Xi]:
                if Xk != Xj:
                    q.append((Xk, Xi)) 
            revised = True
    return revised
        
def revise(self, Xi, Xj):
    revised = False
    for x in self.domains[Xi]:
        needToRevise = True
        for y in self.domains[Xj]:
            if y != x:
                needToRevise = False
        if needToRevise:
            self.domains[Xi].remove(x)
            revised = True
    return revised

"""
remove illegal values from each square's domain based on arithmetic box constraints
"""
def AC3Constraints(self):
    revised = False
    q = deque()
    for var in self.constraints:
        q.append((var, list(self.constraints[var][2:])))
    while q:
        (Xi, Xj) = q.popleft()
        if self.reviseConstraints(Xi, Xj):
            assert len(self.domains[Xi]) > 0
            for Xk in Xj:
                q.append((Xk, list(self.constraints[Xk][2:])))
            revised = True
    return revised

def reviseConstraints(self, Xi, Xj):
    revised = False
    operation = self.constraints[Xi][0]
    target = self.constraints[Xi][1]
    if len(Xj) == 1:
        for x in self.domains[Xi]:
            needToRevise = True
            for Xk in Xj:
                for y in self.domains[Xk]:
                    if operation == '+':
                        if x + y == target:
                            needToRevise = False
                    if operation == '*':
                        if x * y == target:
                            needToRevise = False
                    if operation == '-':
                        if x - y == target or y - x == target:
                            needToRevise = False
                    if operation == '/':
                        if x / y == target or y / x == target:
                            needToRevise = False
            if needToRevise:
                self.domains[Xi].remove(x)
                revised = True
    else:
        domains = []
        for Xk in Xj:
            domains.append(self.domains[Xk])
        fullDomain = list(itertools.product(*domains))
        possibleValues = []
        for x in self.domains[Xi]:
            needToRevise = True
            if operation == '+':
                for i in range(len(fullDomain)):
                    possibleValues.append(self.addValue(fullDomain[i]))
                for y in possibleValues:
                    if x + y == target:
                        needToRevise = False
            elif operation == '*':
                for i in range(len(fullDomain)):
                    possibleValues.append(self.multiplyValue(fullDomain[i]))
                for y in possibleValues:
                    if x * y == target:
                        needToRevise = False
            if needToRevise:
                self.domains[Xi].remove(x)
                revised = True
    return revised

"""
Runs both AC3 algorithms until no further changes are made
"""
def AC3Prep(self):
    reg_revised = True
    constraint_revised = True
    while not self.isAssignmentComplete() and (reg_revised or constraint_revised) :
        for var in self.domains:
            if len(self.domains[var]) == 1:
                self.assignment[var[0]][var[1]] = self.domains[var][0]
            if len(self.domains[var]) == 0:
                return "Unsolvable"
        reg_revised = self.AC3()
        constraint_revised = self.AC3Constraints()
```
### Checking Node Consistency
When we run backtrack search, after we assign each node a value we need to check if the assignment is still consistent. If it is, we continue down the current path, and if it isn't we abandon the path and backtrack to the last consistent state. Before assigning a value to a node, we need to check the following:
Node Consistency - the node is being assigned a valid value from its domain
Row/Column Arc Consistency - the value being assigned isn't already taken by another node on the same row or column
Arithmetic Box Arc Consistency - It is still possible to achieve the target value given the operation and the assigned or possible values of other nodes in the box

```
def isAssignmentConsistent(self, Xi, x):
    assignment = copy.deepcopy(self.assignment)
    assignment[Xi[0]][Xi[1]] = x
    isConsistent = True
    if not self.isNodeConsistent(assignment, Xi):
        isConsistent = False
    for Xj in self.arcs[Xi]:
        if not self.isArcConsistent(assignment, Xi, Xj):
            isConsistent = False
    if not self.isNodeConstraintConsistent(assignment, Xi):
        isConsistent = False
    return isConsistent          

"""
Checks if square's assignment is consistent with arithmetic box
    - if neighbor(s) are already assigned, 
    value must be consistent with target value
    - if neighbor(s) have not been assigned,
    value must allow for possible achievement of target value
"""
def isNodeConstraintConsistent(self, assignment, Xi):
    isConsistent = False
    operation = self.constraints[Xi][0]
    target = self.constraints[Xi][1]
    Xj = list(self.constraints[Xi][2:])
    if len(Xj) == 1:
        if assignment[Xj[0][0]][Xj[0][1]] == 0:
            for y in self.domains[Xj[0]]:
                if operation == '+':
                    if assignment[Xi[0]][Xi[1]] + y == target:
                        isConsistent = True
                elif operation == '*':
                    if assignment[Xi[0]][Xi[1]] * y == target:
                        isConsistent = True
                elif operation == '-':
                    if (assignment[Xi[0]][Xi[1]] - y == target or
                        y - assignment[Xi[0]][Xi[1]] == target):
                        isConsistent = True
                elif operation == '/':
                    if (assignment[Xi[0]][Xi[1]] / y == target or
                        y / assignment[Xi[0]][Xi[1]] == target):
                        isConsistent = True
        else:
            if operation == '+':
                if assignment[Xi[0]][Xi[1]] + assignment[Xj[0][0]][Xj[0][1]] == target:
                    isConsistent = True
            elif operation == '*':
                if assignment[Xi[0]][Xi[1]] * assignment[Xj[0][0]][Xj[0][1]] == target:
                    isConsistent = True
            elif operation == '-':
                if (assignment[Xi[0]][Xi[1]] - assignment[Xj[0][0]][Xj[0][1]] == target or
                    assignment[Xj[0][0]][Xj[0][1]] - assignment[Xi[0]][Xi[1]] == target):
                    isConsistent = True
            elif operation == '/':
                if (assignment[Xi[0]][Xi[1]] / assignment[Xj[0][0]][Xj[0][1]] == target or
                    assignment[Xj[0][0]][Xj[0][1]] / assignment[Xi[0]][Xi[1]] == target):
                    isConsistent = True                    
    else:
        domains = []
        for Xk in Xj:
            if assignment[Xk[0]][Xk[1]] == 0:
                domains.append(self.domains[Xk])
            else:
                domains.append([assignment[Xk[0]][Xk[1]]])
        fullDomain = list(itertools.product(*domains))
        possibleValues = []
        if operation == '+':
            for i in range(len(fullDomain)):
                possibleValues.append(self.addValue(fullDomain[i]))
            for y in possibleValues:
                if assignment[Xi[0]][Xi[1]] + y == target:
                    isConsistent = True
        elif operation == '*':
            for i in range(len(fullDomain)):
                possibleValues.append(self.multiplyValue(fullDomain[i]))
            for y in possibleValues:
                if assignment[Xi[0]][Xi[1]] * y == target:
                    isConsistent = True
    return isConsistent

def isNodeConsistent(self, assignment, Xi):
    if (assignment[Xi[0]][Xi[1]] >= 0 and 
        assignment[Xi[0]][Xi[1]] <= self.size):
        return True
    else:
        return False

def isArcConsistent(self, assignment, Xi, Xj):
    if assignment[Xi[0]][Xi[1]] != self.assignment[Xj[0]][Xj[1]]:
        return True
    else:
        return False
```
### Putting It All Together
Now we are ready to run backtrack search! A final optimization is to choose the node with the smallest domain at each step of the search. This will cause failures to occur quicker, and we will be able to prune more paths from the search tree. This can be very important, because in a 9 /times 9 grid there could be 9^81 possible assignments, which would take literally forever to try!
```
def backtrackSearch(self):
    if self.backtrack() != "failure":
        self.display()
    else:
        print("Could not solve")

"""
Backtrack search - attempts to complete assignment,
backtracks if dead end reached
"""
def backtrack(self):
    if self.isAssignmentComplete():
        return self.assignment
    var = self.selectUnassignedVariable()
    for value in self.orderDomainValues(var):
        if self.isAssignmentConsistent(var, value):
            self.assignment[var[0]][var[1]] = value
            result = self.backtrack()
            if result != "failure":
                return result
            self.assignment[var[0]][var[1]] = 0
    return "failure"
```
