import random
import math
import json
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

class GibbsSampler():
    def __init__(self):
        self.N = 100
        self.answer = 0
        self.classVariable = None
        self.query = []
        self.bnData = []
        self.indexNodes = []
        self.priorSamplingList = []
        self.averageValues = []
        self.stationaryValues = []
        self.markovBlankets = {}
        self.bayesianNetwork = {}
        self.evidenceDictionary = {}
        
    def inputData(self, fileName):
        #fucking json
        file = open(fileName)
        self.bnData = json.load(file)
        for x in range(len(self.bnData)):
            self.bayesianNetwork[self.bnData[x][0]] = Node(self.bnData[x][0], self.bnData[x][1], self.bnData[x][2])
        #populate indexNode list
        for node in self.bnData:
            self.indexNodes.append(node[0])
   
    def inputQuery(self, file):
        f = open(file)
        self.query = json.load(f)
        self.classVariable = self.query[0]
        for i in range(len(self.query[1])):
            self.evidenceDictionary[self.query[1][i]] = self.query[2][i]

    def randomChoice(self, prob):
        temp = []
        for x in range(int(prob * 100)):
            temp.append(True)
        for y in range(int((1 - prob) * 100)):
            temp.append(False)
        return random.choice(temp)

    def initializeMarkovBlankets(self):
        #find markov blankets
        for node in self.bnData:
            if not self.evidenceDictionary.has_key(node[0]):
                temp = []
                for markovBlanky in self.bnData:
                    if node[0] == markovBlanky[0]:
                        temp.extend(markovBlanky[1])
                    else:
                        if markovBlanky[1].count(node[0]) > 0:
                            if temp.count(markovBlanky[0]) == 0:
                                temp.append(markovBlanky[0])
                            for parent in markovBlanky[1]:
                                if parent != node[0] and temp.count(parent) == 0:
                                    temp.append(parent)
                self.markovBlankets[node[0]] = temp
            
    def computeGibbs(self, total):
        stateChange = 0
        counter = 0
        visitTrue = 0
        visitFalse = 0
        prevValue = 0
        while True:
            counter += 1
            self.priorSamplingList = []
            #generate random prior list
            for randomListValue in range(len(self.indexNodes)):
                self.priorSamplingList.append(self.randomChoice(0.5))
            #hardcode evidence variables
            for key, value in self.evidenceDictionary.iteritems():
                self.priorSamplingList[self.indexNodes.index(key)] = value
            stateChange += 1
            if self.priorSamplingList[self.indexNodes.index(self.classVariable[0])] == True:
                visitTrue += 1
                #print self.priorSamplingList
            #initialize markov blankets
            self.initializeMarkovBlankets()
            #compute state of nonevidence variables using markov blanket
            for keys, values in self.bayesianNetwork.iteritems():
                mbProduct = 1
                if not self.evidenceDictionary.has_key(keys):
                    for key, blanket in self.markovBlankets.iteritems():
                        #add key to markov blanket to do computation
                        blanket.append(key)
                        for item in blanket:
                            node = self.bayesianNetwork.get(item)
                            for cpt in node.CPT:
                                temp = []
                                for parent in range(len(node.parents)):
                                    temp.append(cpt[parent])
                                #create a list of key to value items
                                tempPSList = []
                                val = None
                                for x in self.indexNodes:
                                    if node.parents.count(x) > 0:
                                        val = self.priorSamplingList[self.indexNodes.index(x)]
                                        tempPSList.append(val)
                                #compare them
                                if temp == tempPSList:
                                    prob = cpt[-1]
                                    mbProduct *= prob
                                    normalized = self.normalizer(blanket, self.priorSamplingList)
                    #now that we found the prob: change the value in priorlist
                    mbProbability = mbProduct / normalized
                    self.priorSamplingList[self.indexNodes.index(self.classVariable[0])] = self.randomChoice(mbProbability)
                    stateChange += 1
                    if self.priorSamplingList[self.indexNodes.index(self.classVariable[0])] == True:
                        visitTrue += 1
                    elif self.priorSamplingList[self.indexNodes.index(self.classVariable[0])] == False:
                        visitFalse += 1
            if counter >= int(total * 0.1):
                self.averageValues.append(self.normalize([visitTrue, visitFalse]))
                if self.stationaryValues.count(self.normalize([visitTrue, visitFalse])) == len(self.stationaryValues):
                    self.stationaryValues.append(self.normalize([visitTrue, visitFalse]))
                if len(self.stationaryValues) > 100:
                    if self.stationaryValues[0] == self.normalize([visitTrue, visitFalse]):
                        break
                    else:
                        self.stationaryValues = []
                self.stationaryValues.append(self.normalize([visitTrue, visitFalse]))
        #average of stationary vals
        av = []
        for x in range(0, len(self.stationaryValues), len(self.stationaryValues) / 10):
            av.append(self.stationaryValues[x][0])
        val = round(math.fsum(av)/len(av), 3)
        xVal = round(1.0 - val, 3)
        self.answer = [val, xVal]
        
    def normalizer(self, blanket, list):
        normalized = 0
        for x in range(2):
            mbProduct = 1
            for item in blanket:
                node = self.bayesianNetwork.get(item)
                for cpt in node.CPT:
                    temp = []
                    for parent in range(len(node.parents)):
                        temp.append(cpt[parent])
                    #create a list of key to value items
                    tempPSList = []
                    val = None
                    for x in self.indexNodes:
                        if node.parents.count(x) > 0:
                            val = list[self.indexNodes.index(x)]
                            tempPSList.append(val)
                    #compare them
                    if temp == tempPSList:
                        if list[self.indexNodes.index(node.name)] == False:
                            prob = 1 - cpt[-1]
                        else:
                            prob = cpt[-1]
                        mbProduct *= prob
            #change the sign and add the value
            normalized += mbProduct
            if list[self.indexNodes.index(node.name)] == True:
                list[self.indexNodes.index(node.name)] = False
            else:
                list[self.indexNodes.index(node.name)] = True

        return normalized
                           
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
    G = GibbsSampler()
    G.inputData(sys.argv[1])
    G.inputQuery(sys.argv[2])
    G.computeGibbs(sys.argv[3])
    print G.answer