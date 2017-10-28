import cv2
import numpy as np
import math
import random
import time

def dist(crds1, crds2): # Manhattan
    (x1, y1) = crds1
    (x2, y2) = crds2
    return abs(y2 - y1) + abs(x2 - x1)

class Map:
    height = 15
    width = 15
    x,y = 8,8
    sx,sy = 8,8
    tx,ty = 0,0
    color_player = [0,100,200]
    color_background = (255,255,255)
    scalar = 20
    mutate_probability = 0.1
    population = []


    def __init__(self):
        self.maxDist = dist((0, 0) , (self.width-1, self.height-1))
        self.sizeOfPath = dist((self.x,self.y),(self.tx,self.ty))
        self.coPoint = random.randint(0, self.sizeOfPath-1)
        self.best = [[], 0]
        self.reset()

    def reset(self):
        self.color_player[0] = (self.color_player[0] + 10) % 255

        self.x, self.y = self.sx, self.sy
        self.scene =  np.zeros((self.height*self.scalar,self.width*self.scalar,3), np.uint8)

        for i in range(0, self.width):
            for j in range(0, self.height):
                cv2.rectangle(self.scene,(int(self.scalar/2)+i*self.scalar,int(self.scalar/2)+j*self.scalar), (int(self.scalar/2)+i*self.scalar,int(self.scalar/2)+j*self.scalar), self.color_background, int(self.scalar/2))
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

    def generatePopulation(self):
        for i in range(0,4):
            self.population.append(np.random.randint(low=1, high=5, size=self.sizeOfPath))

    def crossOver(self, p1, p2):
        self.coPoint = random.randint(0, self.sizeOfPath-1)
        np1 = list(p1[:self.coPoint]) + list(p2[-(len(p2)-self.coPoint):])
        np2 = list(p2[:self.coPoint]) + list(p1[-(len(p1)-self.coPoint):])

        self.p1 = np1
        self.p2 = np2
        self.population.append(self.p1)
        self.population.append(self.p2)
        return (p1, p2)

    def tryMutation(self):
        i = 0
        happen = False
        for path in self.p1:
            if(random.random() < self.mutate_probability):
                happen = True
                self.p1[i] = random.randint(1, 4)
            i += 1

        if(happen):
            self.population.append(self.p1)

        i = 0
        happen = False
        for path in self.p2:
            if(random.random() < self.mutate_probability):
                happen = True
                self.p2[i] = random.randint(1, 4)
            i += 1

        if(happen):
            self.population.append(self.p2)

    def eliminate(self):
        fitnesses = []
        for path in self.population:
            fitness = self.fitnessOfPath(path)
            if(self.best[1] < fitness):
                self.best = [path, fitness]
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
            print(str(i) + ": " + str(self.best[1]))
            i += 1
            self.showPath(self.best[0])

        return self.best[0]

map = Map()
#print(map.fitnessOfPath([3,3,3,3,3]))
path = map.generatePath()
print(map.resultOfPath(map.best[0]))
print(map.best[0])
cv2.waitKey(0)
cv2.destroyAllWindows()
