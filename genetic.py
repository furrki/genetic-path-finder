import cv2
import numpy as np
import math
import random
import time
import copy
def dist(crds1, crds2): # Manhattan
    (x1, y1) = crds1
    (x2, y2) = crds2
    return abs(y2 - y1) + abs(x2 - x1)

class Map:
    height = 10
    width = 10
    x,y = 5,5
    sx,sy = 5,5
    tx,ty = 0,0
    color_player = [0,100,200]
    color_background = (255,255,255)
    color_barreer = (30,30,30)
    scalar = 20
    mutate_probability = 0.3
    population = []
    barreers = []
    eta = 0
    def __init__(self):
        self.maxDist = dist((0, 0) , (self.width-1, self.height-1))
        self.sizeOfPath = 2*dist((self.x,self.y),(self.tx,self.ty))

        self.coPoint = random.randint(0, self.sizeOfPath-1)
        self.best = [[], 0]
        self.reset()

    def reset(self):

        self.x, self.y = self.sx, self.sy
        self.scene =  np.zeros((self.height*self.scalar,self.width*self.scalar,3), np.uint8)

        for i in range(0, self.width):
            for j in range(0, self.height):
                cv2.rectangle(self.scene,(int(self.scalar/2)+i*self.scalar,int(self.scalar/2)+j*self.scalar), (int(self.scalar/2)+i*self.scalar,int(self.scalar/2)+j*self.scalar), self.color_background, int(self.scalar/2))

        for barreer in self.barreers:
            cv2.rectangle(self.scene,(int(self.scalar/2)+barreer[0]*self.scalar,int(self.scalar/2)+barreer[1]*self.scalar), (int(self.scalar/2)+barreer[0]*self.scalar,int(self.scalar/2)+barreer[1]*self.scalar), self.color_barreer, int(self.scalar/2))



        cv2.rectangle(self.scene,(int(self.scalar/2) + self.tx*self.scalar, int(self.scalar/2) + self.ty*self.scalar),(int(self.scalar/2) + self.tx*self.scalar, int(self.scalar/2) + self.ty*self.scalar),(0,255,0),int(self.scalar/2))
        cv2.rectangle(self.scene,(int(self.scalar/2) + self.sx*self.scalar, int(self.scalar/2) + self.sy*self.scalar),(int(self.scalar/2) + self.sx*self.scalar, int(self.scalar/2) + self.sy*self.scalar),(0,0,255),int(self.scalar/2))

    def refresh(self):
        cv2.circle(self.scene,(int(self.scalar/2) + self.x*self.scalar, int(self.scalar/2) + self.y*self.scalar), int(self.scalar/2), self.color_player, -1)
        cv2.imshow("scene",self.scene)
        if(self.best[1] == 1.0):
            time.sleep(.3)

        time.sleep(.01)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("asd")

    def doMove(self, move):
        # 1-Left 2-Top 3-Right 4- Bottom
        # 1- (-1,0) 2- (0,1) 3- (1,0) 4- (0,-1)
        if(move == 1):
            self.x += -1
        elif(move == 2):
            self.y += 1
        elif(move == 3):
            self.x += 1
        elif(move == 4):
            self.y += -1

    def showPath(self,path):
        self.reset()
        self.refresh()
        for move in path:
            self.doMove(move)
            self.refresh()

    def doPath(self, path):
        self.refresh()
        for move in path:
            self.doMove(move)
            self.refresh()

    def resultOfMove(self, startingPoint, move):
        (x,y) = startingPoint
        # 1-Left 2-Top 3-Right 4- Bottom
        # 1- (-1,0) 2- (0,1) 3- (1,0) 4- (0,-1)
        if(move == 1):
            x += -1
        elif(move == 2):
            y += 1
        elif(move == 3):
            x += 1
        elif(move == 4):
            y += -1
        return (x, y)

    def resultOfPath(self,path):
        self.reset()
        (x, y) = (self.x, self.y)
        for move in path:
            (x,y) = self.resultOfMove((x,y), move)
        return (x,y)

    def fitnessOfPath(self, path):
        self.reset()
        (x, y) = (self.x, self.y)
        for move in path:
            (x,y) = self.resultOfMove((x,y), move)
        distance = dist((x, y), (self.tx, self.ty))
        return (self.maxDist - distance)/self.maxDist

    def checkPoint(self, startingPoint):
        (x, y) = startingPoint
        if(x < 0 or y < 0 or x > self.width or y > self.height):
            return False

        for barreer in self.barreers:
            if(barreer[0] == x and barreer[1] == y):

                return False
        return True

    def checkMove(self, startingPoint, move):


        return self.checkPoint(self.resultOfMove(startingPoint ,move))

    def checkPath(self, path):
        self.reset()
        (x, y) = (self.x, self.y)
        for move in path:
            if(not self.checkMove((x,y),move)):
                return False
            (x,y) = self.resultOfMove((x,y), move)
        return True

    def generateRandomArray(self):
        r = []
        for i in range(0,self.sizeOfPath):
            move = random.randint(1,4)
            r.append(move)
        return r

    def generatePopulation(self):
        for i in range(0,4):
            path = self.generateRandomArray()
            while not self.checkPath(path):
                path = self.generateRandomArray()
            self.population.append(path)

    def crossOver(self, p1, p2):
        self.coPoint = random.randint(0, self.sizeOfPath-1)
        np1 = list(p1[:self.coPoint]) + list(p2[-(len(p2)-self.coPoint):])
        np2 = list(p2[:self.coPoint]) + list(p1[-(len(p1)-self.coPoint):])
        self.p1 = np1
        self.p2 = np2
        while not (self.checkPath(np1) and self.checkPath(np2)):

            self.coPoint = random.randint(0, self.sizeOfPath-1)
            np1 = list(self.p1[:self.coPoint]) + list(self.p2[-(len(self.p2)-self.coPoint):])
            np2 = list(self.p2[:self.coPoint]) + list(self.p1[-(len(self.p1)-self.coPoint):])
            self.tryMutation()


        self.population.append(self.p1)
        self.population.append(self.p2)
        return (p1, p2)

    def tryMutation(self):
        tmpp1 = copy.copy(self.p1)
        tmpp2 = copy.copy(self.p2)
        i = 0
        happen = False
        for path in tmpp1:
            if(random.random() < self.mutate_probability):
                happen = True
                tmpp1[i] = random.randint(1, 4)
            i += 1
        while not self.checkPath(tmpp1):

            i = 0
            happen = False
            for path in tmpp1:
                if(random.random() < self.mutate_probability):
                    happen = True
                    tmpp1[i] = random.randint(1, 4)
                i += 1
        if(happen  ):
            self.p1 = tmpp1
            self.population.append(tmpp1)

        i = 0
        happen = False
        for path in tmpp2:
            if(random.random() < self.mutate_probability):
                happen = True
                tmpp2[i] = random.randint(1, 4)
            i += 1

        while not self.checkPath(tmpp2):

            i = 0
            happen = False
            for path in tmpp2:
                if(random.random() < self.mutate_probability):
                    happen = True
                    tmpp2[i] = random.randint(1, 4)
                i += 1
        if(happen):
            self.p2 = tmpp2
            self.population.append(tmpp2)

    def eliminate(self):
        fitnesses = []
        for path in self.population:
            fitness = self.fitnessOfPath(path)

            if(self.best[1] < fitness+self.eta):
                self.best = [path, fitness]
                self.showPath(self.best[0])
            fitnesses.append(fitness)

        maxIndex = fitnesses.index(max(fitnesses))
        p1 = self.population[maxIndex]

        maxIndex = fitnesses.index(sorted(fitnesses, reverse=True)[1])
        p2 = self.population[maxIndex]

        self.population = []
        self.crossOver(p1, p2)
        self.tryMutation()

    def generatePath(self):
        self.generatePopulation()
        i = 0
        while(self.best[1] < 1.0):
            self.eliminate()
            if(i % 200 == 0):
                self.showPath(self.best[0])

            print(str(i) + ": " + str(self.best[1]))
            i += 1
            if(i % 1000 == 0):
                self.eta += 0.5

            if(i % 1003 == 0):
                self.eta -= 0.5

        return self.best[0]

    def addBarreer(self, x, y):
        self.barreers.append((x,y))

mmap = Map()
#print(map.fitnessOfPath([3,3,3,3,3]))
mmap.addBarreer(1,1)
mmap.addBarreer(1,2)
mmap.addBarreer(1,3)

mmap.addBarreer(3,2)
mmap.addBarreer(4,4)
path = mmap.generatePath()
print(mmap.resultOfPath(mmap.best[0]))
print(mmap.best[0])
cv2.waitKey(0)
cv2.destroyAllWindows()
