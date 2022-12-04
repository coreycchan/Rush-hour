import heapq
import time
from sys import argv, stdout

#priority queue used to implement my search functions
class PriorityQueue: 
    def __init__(self): 
        self.heap = []

    def push(self, item, index, priority):
        pair = (priority, index, item)
        heapq.heappush(self.heap, pair)

    def pop(self): 
        (priority, index, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0 

    def __lt__(self, other):
        return self.heap[0][0] < other.heap[0][0]

    def __le__(self, other):
        return self.heap[0][0] <= other.heap[0][0]
 
    def __eq__(self, other):
        return self.heap[0][0] == other.heap[0][0]

    def __gt__(self, other):
        return self.heap[0][0] > other.heap[0][0]

    def __ge__(self, other):
        return self.heap[0][0] >= other.heap[0][0]


class Grid:
    def __init__(self, width, height, exitRow):
        self.width = width
        self.height = height
        self.exitRow = exitRow
        self.traffic = set()
        self.special = None
        self.occupied = set()

    #add a vehicle to the existing grid
    def addVehicle(self, v):
        self.traffic.add(v)
        if v.id == 'A':
            self.special = v
        self.occupiedSpaces() 

    #get a vehicle at some position, used for heuristics
    def vehicleAt(self, position):
        for v in self.traffic: 
            if v.position[0] != position[0] and v.position[1] != position[1]:
                continue
            else:
                if position in v.occupiedSpaces():
                    return v
        return None

    def getVehicle(self, id):
        for v in self.traffic: 
            if v.id == id: 
                return v 
        return None

    #returns a set of all occupied spaces on the grid
    def occupiedSpaces(self):
        occupied = set() 
        for v in self.traffic: 
            occupied = v.occupiedSpaces() | occupied
        self.occupied = occupied
        return occupied

    #list of all valid moves given some grid
    def allMoves(self):
        moves = []
        for v in self.traffic:
            moves.extend(v.validMoves())
        return moves

    #returns a list of all cars and there current start positions
    def state(self):
        state = []
        for v in self.traffic:
            state.append((v.id, v.position))
        state.sort()
        return state 

    def loadState(self, state):
        for v in state: 
            self.getVehicle(v[0]).position = v[1]

    def makeMove(self, move):
        v = self.getVehicle(move[0])
        v.move(move[1], move[2])

    #print grid in terminal
    def printGrid(self):
        for r in range(self.width + 1):
            for c in range(self.height + 1):
                if r == 0:
                    if c == 0:
                        stdout.write(" ")
                    else:
                        stdout.write(str(c))
                    stdout.write("  ")
                else:
                    if c != 0:
                        vehicle = self.vehicleAt( (c, r) )
                        if vehicle == None:
                            stdout.write(" ")
                        else:
                            stdout.write(vehicle.id)
                    else:
                        stdout.write(str(r))
                    stdout.write("  ")
            if r == self.exitRow:
                stdout.write(">> exit")
            stdout.write("\n\n")

    #write the grid to a txt file
    def writeGrid(self, path):
        f = open(path, 'a')
        for r in range(self.width + 1):
            for c in range(self.height + 1):
                if r == 0:
                    if c == 0:
                        f.write(" ")
                    else:
                        f.write(str(c))
                    f.write("  ")
                else:
                    if c != 0:
                        vehicle = self.vehicleAt( (c, r) )
                        if vehicle == None:
                            f.write(" ")
                        else:
                            f.write(vehicle.id)
                    else:
                        f.write(str(r))
                    f.write("  ")
            if r == self.exitRow:
                f.write(">> exit")
            f.write("\n\n")

    #determining if the board is in the final state, ie ambulance AA at the exit
    def isFinished(self):
        if self.special.orientation == "right" and self.special.position[0] + self.special.length - 1 == self.width:
            return True
        elif self.special.orientation == "left" and self.special.position[0] == self.width: 
            return True
        else:
            return False

class Vehicle: 
    def __init__(self, id, length, position, orientation, fuel, grid):
        self.id = id
        self.length = length
        self.position = position
        self.orientation = orientation
        self.grid = grid
        self.fuel = fuel
        grid.addVehicle(self)

    #move the car and update occupied spaces
    def move(self, distance, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - distance)
            self.fuel = int(self.fuel) - 1
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + distance)
            self.fuel = int(self.fuel) - 1
        elif direction == "left":
            self.position = (self.position[0] - distance, self.position[1])
            self.fuel = int(self.fuel) - 1
        elif direction == "right":
            self.position = (self.position[0] + distance, self.position[1])
            self.fuel = int(self.fuel) - 1
        self.grid.occupiedSpaces()

    #find all valid moves for a given car
    def validMoves(self):
        taken = self.grid.occupied - self.occupiedSpaces()
        savedPosition = self.position
        validMoves = []
        if self.orientation == "left" or self.orientation == "right":
            distance = 1
            start = self.position[0] if self.orientation == "right" else self.position[0] - self.length + 1
            while start > 1:
                self.position = (self.position[0] - 1, self.position[1])
                if taken & self.occupiedSpaces() == set() and self.fuel != '0':
                    validMoves.append([self.id, distance, "left"])
                else: 
                    distance = 0
                    break
                start -= 1
                distance += 1 
            self.position = savedPosition
            end = self.position[0] if self.orientation == "left" else self.position[0] + self.length - 1
            distance = 1
            while end < self.grid.width:
                self.position = (self.position[0] + 1, self.position[1])
                if taken & self.occupiedSpaces() == set() and self.fuel != '0':
                    validMoves.append([self.id, distance, "right"])
                else: 
                    distance = 0 
                    break
                end += 1
                distance += 1 
            self.position = savedPosition
        elif self.orientation == "up" or self.orientation == "down":
            distance = 1
            start = self.position[1] if self.orientation == "down" else self.position[1] - self.length + 1
            while start > 1:
                self.position = (self.position[0], self.position[1] - 1)
                if taken & self.occupiedSpaces() == set() and self.fuel != '0':
                    validMoves.append([self.id, distance, "up"])
                else:
                    distance = 0
                    break
                start -= 1
                distance += 1
            self.position = savedPosition
            end = self.position[1] if self.orientation == "up" else self.position[1] + self.length - 1
            distance = 1
            while end < self.grid.height: 
                self.position = (self.position[0], self.position[1] + 1)
                if taken & self.occupiedSpaces() == set() and self.fuel != '0':
                    validMoves.append([self.id, distance, "down"])
                else: 
                    distance = 0
                    break
                end += 1
                distance += 1
            self.position = savedPosition
        else: 
            raise TypeError('orientation')
        return validMoves

    #find all occupied spaces
    def occupiedSpaces(self):
        occupied = set() 
        for i in range(self.length):
            if self.orientation == "up":
                occupied.add((self.position[0], self.position[1] - i))
            elif self.orientation == "down":
                occupied.add((self.position[0], self.position[1] + i))
            elif self.orientation == "left":
                occupied.add((self.position[0] - i, self.position[1]))
            elif self.orientation == "right":
                occupied.add((self.position[0] + i, self.position[1]))
        return occupied

    def printInfo(self):
        print("Vehicle " + str(self.id) + "\tSize: 1 x " + str(self.length) + "\tAt: " + str(self.position) + "\tOrientation: " + str(self.orientation))

class Search:
    def __init__(self, grid):
        self.fringe = PriorityQueue()
        self.map = dict()
        self.grid = grid
        self.expandedNodes = 0
        self.bfs = 0

    def useBFS(self, bfs):
        self.bfs = bfs

    def costOfMoves(self, moveList):
        return 1 * len(moveList)

    def aStarSearch(self, path):
        st = time.time()
        # Start with initial state
        #self.grid.writeGrid(path)
        index = 0
        initialState = self.grid.state()
        self.map[str(initialState)] = []
        #load all moves given the initial state
        for move in self.grid.allMoves():
            g_cost = self.costOfMoves(self.map[str(initialState)]) + 1
            if self.bfs == '1': 
                h_cost = self.heuristicBlockingCars(move, initialState)
            elif self.bfs == '2':
                h_cost = self.heuristicConstant(move, initialState)
            elif self.bfs == '3':
                h_cost = self.heuristicBlockingPositions(move, initialState)
            elif self.bfs == '4':
                h_cost = self.heuristicBlockingCars(move, initialState) + self.heuristicBlockingPositions(move, initialState)
            else:
                #this represents UCS as it only takes into account g(h) at line 282
                h_cost = self.nullHeuristic(move, initialState) 
            self.fringe.push((move, initialState), index, g_cost + h_cost)
            index += 1
            
        # The actual algorithm
        #finished check, because the board can start in a finished state
        if self.grid.isFinished():
            et = time.time()
            elapsed_time = et - st
            f = open(path, 'a')
            f.write("Runtime: " + str(elapsed_time) + " seconds\t")
            f.write("Expanded %i positions" % self.expandedNodes + "\t")
        
            #self.grid.writeGrid(path)

            return self.map[str(self.grid.state())]
        
        #while there are still moves that can be made and not seen yet
        while not self.fringe.isEmpty():
            move = self.fringe.pop()
            self.grid.loadState(move[1])
            self.grid.makeMove(move[0])
            newState = self.grid.state()
            

            # If this state has been visited
            if str(newState) in self.map:
                continue
            else:
                self.expandedNodes += 1
                #print move[0]
                newMoveList = self.map[str(move[1])][:]
                newMoveList.append(move[0])
                self.map[str(newState)] = newMoveList

                if self.grid.isFinished():
                    et = time.time()
                    elapsed_time = et - st
                    f = open(path, 'a')
                    f.write("Runtime: " + str(elapsed_time) + " seconds\t")
                    f.write("Expanded %i positions" % self.expandedNodes + "\t")

                    #self.grid.writeGrid(path)
                    self.grid.loadState(initialState)                    
                    return self.map[str(newState)]

                for move in self.grid.allMoves():
                    g_cost = self.costOfMoves(self.map[str(newState)]) + 1
                    if self.bfs == '1':
                        h_cost = self.heuristicBlockingCars(move, newState)
                    elif self.bfs == '2':
                        h_cost = self.heuristicConstant(move, newState)
                    elif self.bfs == '3':
                        h_cost = self.heuristicBlockingPositions(move, newState)
                    elif self.bfs == '4':
                        h_cost = self.heuristicBlockingCars(move, newState) + self.heuristicBlockingPositions(move, newState)
                    else:
                        h_cost = self.nullHeuristic(move, newState)
                    self.fringe.push((move, newState), index, g_cost + h_cost)
                    index += 1
        et = time.time()
        elapsed_time = et - st
        f = open(path, 'a')
        f.write("Runtime: " + str(elapsed_time) + "seconds\t")
        f.write("Expanded %i positions" % self.expandedNodes + "\t")
        f.write("Exhausted Fringe\t")
        return []

    def greedySearch(self, path):
        st = time.time()
        #self.grid.writeGrid(path)
        # Start with initial state
        index = 0
        initialState = self.grid.state()
        self.map[str(initialState)] = []
        #there is no g(h) when trying to find f(h), only takes into account h(h)
        for move in self.grid.allMoves():
            if self.bfs == '1': 
                h_cost = self.heuristicBlockingCars(move, initialState)
            elif self.bfs == '2':
                h_cost = self.heuristicConstant(move, initialState)
            elif self.bfs == '3':
                h_cost = self.heuristicBlockingPositions(move, initialState)
            elif self.bfs =='4':
                h_cost = self.heuristicBlockingCars(move, initialState) + self.heuristicBlockingPositions(move, initialState)
            else:
                h_cost = self.nullHeuristic(move, initialState)
            self.fringe.push((move, initialState), index, h_cost)
            index += 1
            
        # The actual algorithm
        if self.grid.isFinished():
            et = time.time()
            elapsed_time = et - st
            f = open(path, 'a')
            f.write("Runtime: " + str(elapsed_time) + " seconds\t")
            f.write("Expanded %i positions" % self.expandedNodes + "\t")
            #self.grid.writeGrid(path)
            return self.map[str(self.grid.state())]
        
        while not self.fringe.isEmpty():
            move = self.fringe.pop()
            self.grid.loadState(move[1])
            self.grid.makeMove(move[0])
            newState = self.grid.state()
            

            # If this state has been visited
            if str(newState) in self.map:
                continue
            else:
                self.expandedNodes += 1
                #print move[0]
                newMoveList = self.map[str(move[1])][:]
                newMoveList.append(move[0])
                self.map[str(newState)] = newMoveList

                if self.grid.isFinished():
                    et = time.time()
                    elapsed_time = et - st
                    f = open(path, 'a')
                    f.write("Runtime: " + str(elapsed_time) + " seconds\t")
                    f.write("Expanded %i positions" % self.expandedNodes + "\t")
                    #self.grid.writeGrid(path)
                    self.grid.loadState(initialState)                    
                    return self.map[str(newState)]
                for move in self.grid.allMoves():
                    if self.bfs == '1':
                        h_cost = self.heuristicBlockingCars(move, newState)
                    elif self.bfs == '2':
                        h_cost = self.heuristicConstant(move, newState)
                    elif self.bfs == '3':
                        h_cost = self.heuristicBlockingPositions(move, newState)
                    elif self.bfs == '4':
                        h_cost = self.heuristicBlockingCars(move, newState) + self.heuristicBlockingPositions(move, newState)
                    else:
                        h_cost = self.nullHeuristic(move, newState)
                    self.fringe.push((move, newState), index, h_cost)
                    index += 1
        et = time.time()
        elapsed_time = et - st
        f = open(path, 'a')
        f.write("Runtime: " + str(elapsed_time) + " seconds\t")
        f.write("Expanded %i positions" % self.expandedNodes + "\t")
        f.write("Exhausted Fringe\t")
        return []


    #h1 heuristic, blocking cars
    def heuristicBlockingCars(self, successor, state):
        # Rank by how many cars in between the special car and exit
        restoreState = self.grid.state()
        self.grid.loadState(state)
        self.grid.makeMove(successor)
        score = 0
        endOfSpecial = self.grid.special.position[0] + self.grid.special.length
        for x in range(endOfSpecial, self.grid.width):
            atLocation = self.grid.vehicleAt((x, self.grid.exitRow))
            if atLocation != None:
                score += 10
                # Break ties by mobility of blocking cars
                score -= 2 * len(atLocation.validMoves())
        if self.grid.isFinished():
            score -= 9999
        self.grid.loadState(restoreState)
        return score

    #h3 heurisitc, blocked positions
    def heuristicBlockingPositions(self, successor, state):
        #rank by how many positions are blocked between the special car and exit
        restoreState = self.grid.state()
        self.grid.loadState(state)
        self.grid.makeMove(successor)
        score = 0
        endOfSpecial = self.grid.special.position[0] + self.grid.special.length
        for x in range(endOfSpecial, self.grid.width):
            atLocation = self.grid.vehicleAt((x, self.grid.exitRow))
            if atLocation != None: 
                score += 10
                if atLocation.orientation == 'right':
                    score * int(atLocation.length)
                #break the ties
                score -= 2 * len(atLocation.validMoves())
        if self.grid.isFinished():
            score -= 9999
        self.grid.loadState(restoreState)
        return score


    #h2 heuristic, blocking cars * some constant, ie 10
    def heuristicConstant(self, successor, state):
        # Rank by how many cars in between the special car and exit
        restoreState = self.grid.state()
        self.grid.loadState(state)
        self.grid.makeMove(successor)
        score = 0
        endOfSpecial = self.grid.special.position[0] + self.grid.special.length
        for x in range(endOfSpecial, self.grid.width):
            atLocation = self.grid.vehicleAt((x, self.grid.exitRow))
            if atLocation != None:
                score += 10
                # Break ties by mobility of blocking cars
                score -= 2 * len(atLocation.validMoves())
        if self.grid.isFinished():
            score -= 9999
        self.grid.loadState(restoreState)
        return score * 10

    #for UCS
    def nullHeuristic(self, successor, state):
        return 0
        
    def printSolution(self, moves):
        initialState = self.grid.state()
        for move in moves:
            print ("Move " + str(move[0]) + " " + str(move[1]) + " space(s) " + move[2])
            self.grid.makeMove(move)
            self.grid.printGrid()
            print("\n")


def readFromFile(filename):
    f = open(filename, 'r')
    line = f.readline()
    data = []
    while line:
        if line[0] == '#':
            line = f.readline()
        elif line.strip() == "":
            line = f.readline()
        else:
            data.append(line)
            line = f.readline()        
    puzzles = []
    for x in data:
        a = x.replace('\n',"")
        a = x.strip()
        puzzles.append(a)    #String of the board with fuel

    return puzzles

def loadCars(puzzle, grid):
    def populateGrid(data):
        data = ''.join([i for i in data if not i.isdigit()])
        grid = [[0]*6 for i in range(6)]
        i = 0
        for x in range(6):
            for y in range(6):
                grid[x][y] = data[i]
                i += 1

        return grid

    def numberOfCars(data):
        cars = []
        a = set(data)
        a.remove('.')
        for x in a:
            if x.strip():
                cars.append(x)
        sortedCars = sorted(cars)
        return sortedCars

    def removeNumbers(data):
        result = ''.join([i for i in data if not i.isdigit()])
        return result

    board = populateGrid(puzzle)
    cars = numberOfCars(removeNumbers(puzzle))
    for car in cars:
        length = []
        coord = []
        fuel = 100
        size = 0
        for i in range(6):
            for j in range(6):
                if car == board[i][j]:
                    length.append(j + 1)
                    length.append(i + 1)

        if length[(len(length) - 1)] - length[1] == 0:
            direction = "right"
            size = length[len(length) - 2] - length[0] + 1
            coord.append(length[0])
            coord.append(length[1])
        elif length[(len(length) - 2)] - length[0] == 0: 
            direction = "down"
            size = length[len(length) - 1] - length[1] + 1
            coord.append(length[0])
            coord.append(length[1])

        for i, elem in enumerate(puzzle):
            if elem.isdigit():
                if puzzle[i - 1] == car:
                    fuel = puzzle[i]
        imported = Vehicle(car, size, coord, direction, fuel, grid)


def writeToFile(path, moves):
    f = open(path, 'a')
    i = 1
    cost = 0

    for move in moves:
        f.write(str(i) + " " + str(move[0]) + " " + str(move[1]) + " " + str(move[2]) + "\n")
        i += 1
        cost += 1
    f.write("cost of path: " + str(cost) + "\n\n")

def writeToFileNoSolution(path, noSolution):
    f = open(path, 'a')
    f.write(noSolution)


if __name__ == "__main__":
    #change input file name
    puzzles = readFromFile("samples-test.txt")
    #change output file name
    write = "output-samples-GBFS-h4.txt"
    index = 1
    for puzzle in puzzles:
        f = open(write, 'a')
        f.write("Puzzle #" + str(index) + ": \tGBFS - h4\t")
        grid = Grid(6,6,3)
        loadCars(puzzle, grid)
        grid.printGrid()
        Solver = Search(grid)
                
        #change this number to change heuristics from 1 - 4, 0 is UCS
        bfsSearch = 4
        Solver.useBFS(bfsSearch)
        moves = Solver.greedySearch(write)
        #uncomment to change Search algorithms
        #moves = Solver.aStarSearch(write)
        if moves != []:
            f.write("Solved in %i moves" % len(moves) + "\t")
            cost = 0
            i = 1
            for move in moves:
                f.write(str(i) + " " + str(move[0]) + " " + str(move[1]) + " " + str(move[2]) + "\n")
                i += 1
                cost += 1
            f.write("cost of path: " + str(cost) + "\n")            
        else:
            noSolution = "No Solution Found"
            f.write(noSolution + "\n")
            print ("No Solution Found\n\n\n")
        index += 1


    


        

                            

    