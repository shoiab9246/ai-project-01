#!/usr/local/bin/python3
# solver2021.py : 2021 Sliding tile puzzle solver
#
# Code by: Name  - Shoiab Mohammed, Vijay Iyer.
#
# Based on skeleton code by D. Crandall, January 2021
#

import sys
import numpy as np
import math

ROWS = 4
COLS = 5


def updatemove(state):
    """
    1. This method is called when the parent or previous node of a successor is to be updated. If this function is called,
    it means that a particular state was reached again, this time with better cost
    2.For every state, 'move' is the move which took place on the board to reach this state. If we check all the successors of
    this reached state, one of them would be the previous state, since this is a board configuration
    """
    for i in successors(state.cameFrom):
        if i.boardConfiguration == state.boardConfiguration:
            return i.move


def reconstructpath(current):
    """
    1. This function is used to retrace the steps or moves we made to reach the goal state.
    2. Since every state has previous state and the move to get to the state from previous state information stored in the
    class object, we can join all the moves from previous states to get the list of moves used to get to current state
    3. We return a reverse of the generated path for printing in the output
    """
    path = []
    while current.cameFrom is not None:
        # print("previous state: \n" + "\n".join(printable_board(tuple(np.ndarray.flatten(np.array(current.boardConfiguration))))))
        path.append(current.move)
        # print("\n")
        current = current.cameFrom

    return path[::-1]


class State:
    """
    Class used to represent any given state on the board. An instance of this class can give all information like
    the boardconfiguration, move made to get to the state, the cost is the number of moves from initial state to get to this state. The fscore is the
    cost plus the value of the heuristic function
    """

    def __init__(self, board, cost, parent, move):
        self.cost = cost
        self.cameFrom = parent
        self.boardConfiguration = board
        self.move = move
        self.fscore = 0

    def get_fscore(self):
        """
        Returns a value which is the sum of the cost function adn heuristic function
        """
        self.fscore = self.cost + self.h1()
        return self.fscore

    def h(self):
        """
        Heuristic Function 1 - Returns a value equal to the number of misplaced numbers on the board/ no. of rows plus columns
        """
        h = 0
        for i in range(len(self.boardConfiguration)):
            for j in range(len(self.boardConfiguration[0])):
                if self.boardConfiguration[i][j] != i * ROWS + (j + 1):
                    h += 1
        return h / (len(self.boardConfiguration) + len(self.boardConfiguration[0]))

    def h1(self):
        """
        Heuristic Function 2 - Sees the distance of each index on the board from goal and then returns an aggregate
        of minimum of the maximum column moves plus maximum row moves.
        """
        board = self.boardConfiguration
        board = np.array(board)

        indexes = [None] * len(board) * len(board[0])
        for i in range(len(board)):
            for j in range(len(board[0])):
                indexes[board[i][j] - 1] = (i, j)
        moves = [[None for _ in range(len(board[0]))] for _ in range(len(board))]
        sum_moves = 0
        count = 0                    # to traverse the indexes list which contains the indexes of all the numbers from 1-20
        for i in range(len(board)):
            for j in range(len(board[0])):
                moves[i][j] = abs(indexes[count][0] - i + indexes[count][1] - j)
                sum_moves += moves[i][j]
                count += 1
        return sum_moves / ((len(board) + len(board[0]))/2)

    def h2(self):
        """
        Heuristic function 3
        """
        moves = 0
        board = np.array(self.boardConfiguration)
        L1 = [i for i in range(1, len(board[0]) + 1)]
        R2 = [i + 5 for i in range(1, len(board[0]) + 1)]
        L3 = [i + 10 for i in range(1, len(board[0]) + 1)]
        R4 = [i + 15 for i in range(1, len(board[0]) + 1)]
        U1 = [(i * 5) + 1 for i in range(len(board))]
        D2 = [(i * 5) + 2 for i in range(len(board))]
        U3 = [(i * 5) + 3 for i in range(len(board))]
        D4 = [(i * 5) + 4 for i in range(len(board))]
        U5 = [(i * 5) + 5 for i in range(len(board))]
        L1_Actual = board[0, :]
        R2_Actual = board[1, :]
        L3_Actual = board[2, :]
        R4_Actual = board[3, :]
        U1_Actual = board[:, 0]
        D2_Actual = board[:, 1]
        U3_Actual = board[:, 2]
        D4_Actual = board[:, 3]
        U5_Actual = board[:, 4]
        moves += 1 if set(L1) == set(L1_Actual) else 0
        moves += 1 if set(R2) == set(R2_Actual) else 0
        moves += 1 if set(L3) == set(L3_Actual) else 0
        moves += 1 if set(R4) == set(R4_Actual) else 0
        moves += 1 if set(U1) == set(U1_Actual) else 0
        moves += 1 if set(D2) == set(D2_Actual) else 0
        moves += 1 if set(U3) == set(U3_Actual) else 0
        moves += 1 if set(D4) == set(D4_Actual) else 0
        moves += 1 if set(U5) == set(U5_Actual) else 0
        return moves


def printable_board(board):
    return [('%3d ') * COLS % board[j:(j + COLS)] for j in range(0, ROWS * COLS, COLS)]


# return a list of possible successor states
def successors(state):
    """
    Returns <no. of rows + no. of columns> successors which are successors at one move difference from the passed state
    """
    successor_states = []
    successor_states.extend([i for i in get_row_moves(state)])
    successor_states.extend([i for i in get_col_moves(state)])
    return successor_states


def get_row_moves(state):
    """
    Returns <no. of rows> successors obtained by making only left or right shifts to the given state
    """
    successor_states = []
    for i in range(len(state.boardConfiguration)):
        newstate = state.boardConfiguration.copy()
        newrow = state.boardConfiguration[i].copy()
        if i == 1 or i == 3:
            newrow.insert(0, newrow.pop())
            move = str('R' + str(i + 1))
        else:
            newrow.append(newrow.pop(0))
            move = str('L' + str(i + 1))
        newstate[i] = newrow
        successor_states.append(State(newstate, math.inf, None, move))

    return successor_states


def get_col_moves(state):
    """
    Returns <no. of columns> successors obtained by making only left or right shifts to the given state
    """
    successor_states = []
    array = np.array(state.boardConfiguration)
    array = np.transpose(array)
    for i in range(len(array)):
        newstate = array.tolist().copy()
        newrow = newstate[i].copy()
        if i == 1 or i == 3:
            newrow.insert(0, newrow.pop())
            move = str('D' + str(i + 1))
        else:
            newrow.append(newrow.pop(0))
            move = str('U' + str(i + 1))
        newstate[i] = newrow
        successor_states.append(State(np.transpose(np.array(newstate)).tolist(), math.inf, None, move))
    return successor_states


def is_goal(state):
    """
    Check if the board is in canonical/sequential order of numbers. Returns a boolean value.
    """
    for i in range(len(state)):
        for j in range(len(state[0])):
            if state[i][j] != i * COLS + (j + 1):
                return False
    return True


def solve(initial_board):
    """
    1. This function should return the solution as instructed in assignment, consisting of a list of moves like ["R2","D2","U1"].
    2. Do not add any extra parameters to the solve() function, or it will break our grading and testing code.
       For testing we will call this function with single argument(initial_board) and it should return 
       the solution.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    board = [[0] * COLS for _ in range(ROWS)]  # used to get board in a 2d list form
    a = iter(list(initial_board))
    for i in range(ROWS):
        for j in range(COLS):
            board[i][j] = next(a)
    state = State(board, 0, None, '')       # creating a state class instance with board as board configuration,
    # cost as 0, previous as None, and move as blank
    if is_goal(state.boardConfiguration):   # checking if initial state itself is the goal
        return state.move
    fringe = [state]                        # fringe variable to keep a list of all nodes considered so far
    move_num = 0
    visited = []

    while fringe:
        current = fringe.pop(fringe.index(min(fringe, key=lambda t: t.get_fscore()))) # assign current as the item in
        # fringe with minimum fscore
        visited.append(current)
        # move_num += 1                                  # used to see the no. of moves states considered so far
        # print(move_num, end=' ')
        # print(printable_board(tuple(np.ndarray.flatten(np.array(current.boardConfiguration)))))
        for i in successors(current):
            present = False
            if is_goal(i.boardConfiguration):           # if goal is reached, update previous state and call path
                # reconstruction method
                i.cameFrom = current
                return reconstructpath(i)

            for item in fringe:                         # check items in fringe, if an exact boardconfiguration in
                # fringe already exists, then this state is an existing state and cost and previous state
                # needs to be updated depending on the value of the cost
                if i.boardConfiguration == item.boardConfiguration:
                    present = True
                    existingState = item
            if present:
                if existingState.cost > current.cost + 1:
                    existingState.cameFrom = current
                    existingState.move = updatemove(existingState)
                    existingState.cost = current.cost + 1
            # since this state hasnt been reached yet, we append it to the fringe
            else:
                # newstate = State(i.boardConfiguration, i.cost + h(i.boardConfiguration),current,i.move)
                i.cameFrom = current
                i.cost = current.cost + 1
                fringe.append(i)

    return reconstructpath(current)  # This line is unreachable since it will only reach here if fringe is empty,
    # having not reached the goal


# Please don't modify anything below this line
#
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        raise (Exception("Error: expected a board filename"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != ROWS * COLS:
        raise (Exception("Error: couldn't parse start state file"))

    print("Start state: \n" + "\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    route = solve(tuple(start_state))

    print("Solution found in " + str(len(route)) + " moves:" + "\n" + " ".join(route))
