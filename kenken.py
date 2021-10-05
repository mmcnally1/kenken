import sys
from collections import deque
import copy
import itertools

'''
Input:
    n - where grid is nxn
    m - number of constraints
    1 constraint per line
        ex. + 2 0,1 0,2
            * 9 2,2 3,2 2,3
            v 4 5,2
'''

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

class KenKenSolver:
    def __init__(self, size):
        self.size = size
        self.assignment = [[0 for i in range(size)] for i in range(size)]
        self.domains = {}
        self.arcs = {}
        self.constraints = {}

    def display(self):
        for i in range(self.size):
            print(self.assignment[i])
    
    '''
    Adds possible values from 1 to n to domain for each position in puzzle
    '''
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
    
    """
    Assigns any values that are given in initial puzzle state
    """
    def createAssignment(self, constraints):
        for i in range(len(constraints)):
            if constraints[i][0] == 'v':
                pos = constraints[i][2]
                self.assignment[pos[0]][pos[1]] = constraints[i][1]

    """
    AC3 algorithm - removes illegal values from each square's domain
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
    Uses AC3 algorithm to remove illegal values from each square's domain based
    on arithmetic box
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

    def isAssignmentComplete(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.assignment[i][j] == 0:
                    return False
        return True

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

    def multiplyValue(self, value):
        val = 1
        for x in value:
            val = val * x
        return val

    def addValue(self, value):
        val = 0
        for x in value:
            val += x
        return val

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
    
    """
    Select unassigned square with lowest number of values in domain
    """
    def selectUnassignedVariable(self):
        min_values = 8
        position = None
        for i in range(self.size):
            for j in range(self.size):
                if self.assignment[i][j] == 0 and len(self.domains[i,j]) < min_values:
                    position = (i,j)
                    min_values = len(self.domains[i,j])
        return position

    def orderDomainValues(self, var):
        return self.domains[var]

if __name__ == "__main__":
    size, numConstraints, constraints = read_input()
    solver = KenKenSolver(size)
    solver.createDomains()
    solver.createArcs()
    solver.addConstraints(constraints)
    solver.createAssignment(constraints)
    print("\n")
    solver.AC3Prep()
    solver.backtrackSearch()
