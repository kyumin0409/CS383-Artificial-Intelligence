import sys
import math
import copy

class Viterbi():
    def __init__(self):
        self.totalFlips = 0
        self.path = []
        # Ft -> Ut
        self.sensorModel = ()
        # Ft-1-> Ft
        self.transitionModel = ()

    def input(self, file):
        f = open(file)
        fair = 0.5
        self.sensorModel = (fair, float(f.readline()))
        probabilityFair = 1 - float(f.readline())
        probabilityUnfair = float(f.readline())
        self.transitionModel = (probabilityFair, probabilityUnfair)
        self.path = f.readline().split()
        f.close()

    def Viterbi(self, index=1, pTrue=1.0, pFalse=0.0, t1=['f'], t2=['f']):
        #base case
        if index == len(self.path):
            if pTrue > pFalse:
                return t1
            else:
                return t2

        #FairFair
        if self.path[index] == 'h':
            a = (pTrue) * (self.transitionModel[0]) * (self.sensorModel[0])
        else:
            a = (pTrue) * (self.transitionModel[0]) * (1 - self.sensorModel[0])

        #FairUnfair
        if self.path[index] == 'h':
            b = (pTrue) * (1.0 - (self.transitionModel[0])) * (self.sensorModel[1])
        else:
            b = (pTrue) * (1.0 - (self.transitionModel[0])) * (1.0 - (self.sensorModel[1]))

        #UnfairFair
        #print 'c',
        if self.path[index] == 'h':
            c = (pFalse) * (self.transitionModel[1]) * (self.sensorModel[0])
        else:
            c = (pFalse) * (self.transitionModel[1]) * (1.0 - (self.sensorModel[0]))

        #UnfairUnfair
        if self.path[index] == 'h':
            d = (pFalse) * (1.0 - (self.transitionModel[1])) * (self.sensorModel[1])
        else:
            d = (pFalse) * (1.0 - (self.transitionModel[1])) * (1.0 - (self.sensorModel[1]))

        #algorithm to detect best choice
        #fair t1
        if a > c:
            bestTrue = a
        else:
            bestTrue = c
            t1 = copy.deepcopy(t2)
        #unfair t2
        if b > d:
            bestFalse = b
            t2 = copy.deepcopy(t1)
        else:
            bestFalse = d
        t1.append('f')
        t2.append('u')

        return self.Viterbi(index+1, bestTrue, bestFalse, t1, t2)

    def printPath(self, path):
        for item in path:
            print str(item),

if __name__ == '__main__':
    V = Viterbi()
    V.input(sys.argv[1])
    path = V.Viterbi()
    V.printPath(path)
    
