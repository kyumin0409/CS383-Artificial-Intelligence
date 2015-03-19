from pprint import pprint
import math
import sys
import copy

class TreeNode():
    def __init__(self, instances):
        self.count = 0
        self.left = None
        self.right = None
        self.leaf = False
        self.cause = []
        self.path = []
        self.entropy = 0
        self.pruned = False
        self.instances = instances
        self.leafDictionary = {'democrat': 0,
                                'republican': 0}
        self.initializeEffects()
        
    def initializeEffects(self):
        for causes in self.leafDictionary.iterkeys():
            self.leafDictionary[causes] = float(0)

    def setEffects(self, cause, count, fraction):
        total = self.instances
        if count > self.instances:
            total = count
        #print total
        self.leafDictionary[cause] += float(fraction) / total

class DecisionTree2():
    def __init__(self):
        self.count = 0
        self.total = 0
        self.instances = 0
        self.entropyList = []
        self.pruning = False
        self.root = TreeNode(self.instances)
        self.root.path.append("root")
        self.causes = {'democrat': 0, 'republican': 0}
        self.dict = {'democrat': 0.0, 'republican': 0.0}
        self.training = {'democrat': {'y': [], 'n': [] },
                         'republican': {'y': [], 'n': []}
                         }

    def inputData(self, file):
        #initialize training dict
        f = open(file)
        line = f.readline().strip('\n').split(',')
        self.instances = len(line[1:])
        for a, b in self.training.iteritems():
            for c, d in b.iteritems():
                for i in range(self.instances):
                    d.append(0.0)
        f.close()

        #count ditribution of classes
        self.file = open(file)
        for lines in self.file.readlines():
            self.total += 1
            lines = lines.strip('\n').split(',')
            cause = lines[0]
            self.causes[cause] += 1
            tree = lines[1:]
            for keys, values in self.training.iteritems():
                if keys == cause:
                    for index in range(len(tree)):
                        for k, v in values.iteritems():
                            if tree[index] == k:
                                v[index] += 1
        self.file.close()
        #start creating the tree
        self.trainingData(file)
        
    def trainingData(self, training):
        train = open(training)
        temp = []
        for item in train.readlines():
            temp.append(item.strip('\n').split(','))
        self.training = copy.deepcopy(temp)
        self.informationGainDT(range(1,self.instances+1), temp, self.root)
        if self.pruning == True:
            self.pruneTree(self.root)

    def informationGainDT(self, indexes, training, node, splitData = []):
        #if training has same values
        if len(training) == 0:
            if node == None:
                node = TreeNode(self.instances)
            return node

        elif self.sameValue(indexes, training):
            if node == None:
                node = TreeNode(self.instances)
            if type(training[0]) != list:
                node.leafDictionary[training[0]] += len(training[1:])
                node.cause.append(training[0])
                node.path.append(training[1])
            else:
                for data in training:
                    node.leafDictionary[data[0]] += len(data[1:])
                    node.cause.append(data[0])
                    node.path.append(data[1])
            node.leaf = True
            return node

        elif len(training) == 2 and self.total != 2:
            if type(training[0]) == list:
                if node == None:
                    node = TreeNode(self.instances)
                return self.informationGainDT(indexes, splitData, node)

        else:
            #this gain will print the index
            index = self.getGain(indexes, training)
            self.entropyList.append(index)
            node.entropy = index
            tempY = []
            splitDataY = []
            tempN = []
            splitDataN = []
            for items in training:
                for item in items[index]:
                    if item == 'y':
                        tempY.append(items[0])
                        splitDataY.append(items)
                    if item == 'n':
                        tempN.append(items[0])
                        splitDataN.append(items)

            [tempY, tempN] = self.ynList([tempY, tempN])

            if node.left == None:
                idx = copy.deepcopy(indexes)
                idx.remove(index)
                node.left = self.informationGainDT(idx, tempY, node.left, splitDataY)
            if node.right == None:
                idex = copy.deepcopy(indexes)
                idex.remove(index)
                node.right = self.informationGainDT(idex, tempN, node.right, splitDataN)

        return node
        
    def ynList(self, tempList):
        for temp in tempList:
            count = 0
            for keys in self.causes.iterkeys():
                if temp.count(keys) > 0:
                    tempo = []
                    tempo.append(keys)
                    for counter in range(temp.count(keys)):
                        count += 1
                        if temp == tempList[0]:
                            tempo.append('y')
                        else:
                            tempo.append('n')
                    temp.append(tempo)
            for counter in range(count):
                temp.pop(0)
        return tempList

    def sameValue(self, indexes, data):
        if len(indexes) == 0:
            return True

        if len(data) >= 2:
            if type(data[0]) == list:
                return False

        result = False
        YorN = []
        for index in range(len(data)):
            YorN.append(data[index][1])
            for index2 in range(len(data[index]) - 1):
                temp = data[index][1:]
                if YorN[0] == temp[index2]:
                    result = True
                else:
                    return False

        if len(set(YorN)) != 1:
            return False
        return result

    def getGain(self, indexList, training):
        bestGain = [0.0, 0]
        for index in indexList:
            #print index
            demY = 0
            demN = 0
            repY = 0
            repN = 0
            for line in training:
                if line[index] == 'y':
                    if line[0] == 'democrat':
                        demY += 1
                    else:
                        repY += 1
                else:
                    if line[0] == 'democrat':
                        demN += 1
                    else:
                        repN += 1

            #print "bEntropy: demY: {0}, demN: {1}".format(demY, demN)
            Y = demY + repY
            N = demN + repN
            if demY == 0 and demN == 0:
                b = 0
            else:
                b = self.bEntropy(float(Y) / (Y + N))
            #print "b: ", b
            r = self.remainder(demY, demN, repY, repN)
            #print "r: ", r
            gain = b - r
            #print "gain: ", gain

            if gain == 1.0:
                bestGain = [gain, index]
                break
            if gain >= bestGain[0]:
                bestGain = [gain, index]

        #print "best gain", bestGain
        return bestGain[1]

    def bEntropy(self, q):
        return -1 * (self.logEntropy(q) + self.logEntropy(1 - q))

    def logEntropy(self, q):
        if q == 0.0:
            return 0
        #log to the base 2
        return q * math.log(q,2)

    def remainder(self, demY, repY, demN, repN):
        dem = demY + demN
        rep = repY + repN
        Y = float(demY + repY)
        N = float(demN + repN)
        
        #print "Remainder: demY: {0}, demN: {1}, repY: {2}, repN: {3}".format(demY, demN, repY, repN)
        if dem + rep == 0:
            return 0
        else:
            if Y == 0 or demY == 0:
                return 0
            else:
                Y = (Y / (dem + rep)) * self.bEntropy(demY / Y)

            if N == 0 or demN == 0:
                return 0
            else:
                N = (N / (dem + rep)) * self.bEntropy(demN / N)

        return Y + N

    def pruneTree(self, node):
        if node.leaf:
            pass

        else:
            pass

    def inputTest(self, file):
        self.file = open(file)
        for lines in self.file.readlines():
            line = lines.strip('\n').split(',')
            #test begins
            line.insert(0, None)
            temp = copy.deepcopy(self.entropyList)
            self.testDecisionTree(line, temp, self.root)

    def testDecisionTree(self, testdata, gainlist, node):
        #base case
        if node == None:
            node = TreeNode(self.instances)
            node.leaf = True

        if node.leaf:
            tempK = []
            tempV = []
            for k, v in node.leafDictionary.iteritems():
                tempK.append(k)
                tempV.append(v)

            if tempV[0] == tempV[1]:
                print "republican" + "," + "0.5"
            else:
                print str(tempK[tempV.index(max(tempV))]) + "," + str(max(tempV)/sum(tempV))
            return

        else:
            index = node.entropy
            vote = testdata[index]
            if vote == 'y':
                self.testDecisionTree(testdata, gainlist, node.left)
            else:
                self.testDecisionTree(testdata, gainlist, node.right)

if __name__ == '__main__':
    D = DecisionTree2()
    D.inputData(sys.argv[1])
    D.inputTest(sys.argv[2])
    if sys.argv[2:] == 'enabled':
        D.pruning = True