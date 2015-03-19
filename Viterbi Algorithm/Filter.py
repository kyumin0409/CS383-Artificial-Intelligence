import sys
import math

class Filter():
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

    def forwardAlgorithm(self, index=1, p=(1.0, 0.0)):
        #base case; if hits end
        if index == len(self.path):
            return p

        #recurse case
        #prediction P(Ft)
        predict = [0,0]
        for i in range(len(p)):
            predict[0] += self.transitionModel[i] * p[i]
            predict[1] += (1 - self.transitionModel[i]) * p[i]
        predict = tuple(predict)
        #print predict[0]

        #update P(Ft|Ut) for true and false
        update = [0,0]
        for i in range(len(predict)):
            if self.path[index] == 'h':
                update[i] = self.sensorModel[i] * predict[i]
            else:
                update[i] = (1 - self.sensorModel[i]) * predict[i]

        update = tuple(self.normalize(update))
        #print update[0]
        
        return self.forwardAlgorithm(index+1, update)

    def forwardAlgorithmWithLog(self, index=1, p=(1.0,0.0)):
        #base case; if hits end
        if index == len(self.path):
            return p
        
        #recurse case; use log prob
        #prediction P(Ft)
        predict = [0,0]
        tmp = [0,0]
        for i in range(len(p)):
            if p[i] == 0.0:
                pi = 0.0
            else:
                pi = math.log(p[i])
            tmp[0] = math.log(self.transitionModel[i]) + pi
            tmp[1] = math.log(1 - self.transitionModel[i]) + pi
            for j in range(len(predict)):
                predict[j] += math.exp(tmp[j])
        predict = tuple(self.normalize(predict))
        print predict[0]

        #update P(Ft|Ut) for true and false
        update = [0,0]
        for i in range(len(predict)):
            if self.path[index] == 'h':
                update[i] = math.log(self.sensorModel[i]) + math.log(predict[i])
            else:
                update[i] = math.log(1 - self.sensorModel[i]) + math.log(predict[i])
        update = (math.exp(update[0]), math.exp(update[1]))
        update = tuple(self.normalize(update))
        print update[0]

        return self.forwardAlgorithmWithLog(index+1, update)

    def normalize(self, update):
        total = sum(update)
        update = [float(update[0])/total, float(update[1])/total]
        return update

if __name__ == '__main__':
    F = Filter()
    testfile = sys.argv[1]
    log = False
    #method call
    F.input(testfile)
    if log:
        prob = str(F.forwardAlgorithmWithLog()).strip('()').split(',')
        print prob[0]
    else:
        prob = str(F.forwardAlgorithm()).strip('()').split(',')
        print prob[0]
