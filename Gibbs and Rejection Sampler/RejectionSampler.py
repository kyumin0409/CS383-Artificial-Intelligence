import random
import json
import math
import sys

class Node():
    def __init__(self, name, parents, values):
        self.total = 0
        self.totalTrue = 0
        self.name = name
        self.parents = parents
        self.values = values
        self.TFList = []
        self.CPT = [[0 for x in xrange(self.total)] for x in xrange(self.total)]
        self.generateCPT()

    def generateTFList(self, iteration):
        total = self.total
        self.TFList = []
        for x in range(total):
            math = (total / 2) / (iteration + 1)
            for xTrue in range(math):
                self.TFList.append(True)
            for xFalse in range(math):
                self.TFList.append(False)
        return self.TFList

    def generateCPT(self):
        #2^n for each table
        self.total = int(math.pow(2, len(self.parents)))
        self.CPT = [[0 for x in xrange(0)] for x in xrange(self.total)]
        #add T & F
        for x in range(len(self.parents)):
            list = self.generateTFList(x)
            for subX in range(self.total):
                self.CPT[subX].append(list.pop(0))
        #add values
        for y in range(self.total):
            self.CPT[y].append(self.values[y])
        
class RejectionSampler():
    def __init__(self):
        self.N = 100
        self.classVariable = None
        self.query = []
        self.bnData = []
        self.indexNodes = []
        self.priorSamplingList = []
        self.bayesianNetwork = {}
        self.evidenceDictionary = {}

    def inputData(self, fileName):
        #fucking json
        file = open(fileName)
        self.bnData = json.load(file)
        for x in range(len(self.bnData)):
            self.bayesianNetwork[self.bnData[x][0]] = Node(self.bnData[x][0], self.bnData[x][1], self.bnData[x][2])
              
    def priorSampling(self, total):
        #creating index list
        for n in self.bnData:
            self.indexNodes.append(n[0])

        #we want to do it N times
        for nSamples in range(total):
            tempDictionary = {}
            for node in self.bnData:
                #if has parents
                if len(node[1]) > 0:
                    prob = 0
                    temp = []
                    for parent in node[1]:
                        temp.append(tempDictionary[parent])
                    #get prob
                    for keys, values in self.bayesianNetwork.iteritems():
                        if keys == node[0]:
                            for cptItems in values.CPT:
                                counter = 0
                                for vals in range(len(temp)):
                                    if temp[vals] == cptItems[vals]:
                                        counter += 1
                                    else:
                                        counter = 0
                                #if row is found
                                if counter == len(temp):
                                    prob = cptItems[-1]
                                    #print temp
                    #add the prob value of item to dict
                    randomValue = self.randomChoice(prob)
                    #print node[0], prob, randomValue
                    tempDictionary[node[0]] = randomValue

                else:
                    randomProb = self.bayesianNetwork.get(node[0]).values[0]
                    randomValue = self.randomChoice(randomProb)
                    #print node[0], randomProb, randomValue
                    tempDictionary[node[0]] = randomValue
            #convert dict to list
            temp = []
            for node in self.bnData:
                for k, v in tempDictionary.iteritems():
                    if k == node[0]:
                        temp.append(v)
            self.priorSamplingList.append(temp)
        
    def randomChoice(self, prob):
        temp = []
        for x in range(int(prob * 100)):
            temp.append(True)
        for y in range(int((1 - prob) * 100)):
            temp.append(False)
        return random.choice(temp)
          
    def inputQuery(self, file):
        f = open(file)
        self.query = json.load(f)
        self.classVariable = self.query[0]
        for i in range(len(self.query[1])):
            self.evidenceDictionary[self.query[1][i]] = self.query[2][i]

    def processInput(self):
        #Given Evidence variables
        if len(self.evidenceDictionary) > 0:
            #reject all evidences
            for k, v in self.evidenceDictionary.iteritems():
                temp = []
                for priors in self.priorSamplingList:
                    if priors[self.indexNodes.index(k)] == v:
                        temp.append(priors)
                self.priorSamplingList = temp
            #compute class variables using accepted list
            self.computeClassVariables(self.priorSamplingList)

        #Given NO evidence variables
        else:
            self.computeClassVariables(self.priorSamplingList)

    def computeClassVariables(self, list):
        cpt = self.generateCPT(self.classVariable)
        answer = []
        for z in cpt:
            counter = 0
            for priors in list:
                for bool in range(len(z)):
                    if priors[self.indexNodes.index(self.classVariable[bool])] == z[bool]:
                        counter += 1
            answer.append(counter)
        print self.normalize(answer)

    def generateTFList(self, total, iteration):
        TFList = []
        for x in range(total):
            math = (total / 2) / (iteration + 1)
            for xTrue in range(math):
                TFList.append(True)
            for xFalse in range(math):
                TFList.append(False)
        return TFList
     
    def generateCPT(self, parents):
        #2^n for each table
        total = int(math.pow(2, len(parents)))
        CPT = [[0 for x in xrange(0)] for x in xrange(total)]
        #add T & F
        for x in range(len(parents)):
            list = self.generateTFList(total, x)
            for subX in range(total):
                CPT[subX].append(list.pop(0))
        return CPT
                           
    def randomFromList(self, list):
        rValue = random.choice(list)
        return rValue

    def normalize(self, list):
        if len(self.priorSamplingList) == 0:
            return []
        else:
            total = sum(list)
            temp = []
            for i in range(len(list)):
                answer = round(float(list[i])/total, 3)
                temp.append(answer)
            return temp
    
if __name__ == '__main__':
    R = RejectionSampler()
    R.inputData(sys.argv[1])
    R.inputQuery(sys.argv[2])
    R.priorSampling(sys.argv[3])
    R.processInput()