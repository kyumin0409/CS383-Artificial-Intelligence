from pprint import pprint
import math

class TreeNode():
    def __init__(self, instances):
        self.count = 0
        self.left = None
        self.right = None
        self.value = None
        self.cause = []
        self.path = []
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

    def fillZeroes(self, cause, count):
        #temp count var
        total = count * 2
        if self.leafDictionary[cause] == 0.0:
            self.leafDictionary[cause] = float(1) / total

class DecisionTree():
    def __init__(self):
        self.total = 0
        self.depth = 0
        self.count = 0
        self.instances = 0
        self.myAlgorithm = True
        self.file = None
        self.queryList = []
        self.posteriorList = []
        self.posterior = {}
        self.root = TreeNode(self.instances)
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
        
    def inputTest(self, file):
        self.file = open(file)
        for lines in self.file.readlines():
            line = lines.strip('\n').split(',')
            self.queryList.append(line)

    def initiateDecisionTree(self, training):
        if self.myAlgorithm == True:
            for keys, values in self.training.iteritems():
                for k, v in values.iteritems():
                    self.DecisionTree(keys, v, [], self.root, 0, k)

        elif self.myAlgorithm == False:
            f = open(training)
            for line in f.readlines():
                line = line.strip('\n').split(',')
                cause = line[0]
                tree = line[1:]
                self.DecisionTreePartTwo(cause, tree, [], self.root, 0, range(1, self.instances), self.queryList)
            self.fillTree(0, [], self.root)
            f.close()

    def DecisionTree(self, cause, tree, temp, node, depth, vote):
        if len(tree) == depth:
            node.path = temp
            return
        else:
            temp.append(vote)
            if node.left == None:
                node.left = TreeNode(self.instances)
            if vote == 'y':
                node.left.setEffects(cause, self.causes[cause], tree[depth])
            self.DecisionTree(cause, tree, temp, node.left, depth+1, vote)

            if node.right == None:
                node.right = TreeNode(self.instances)
            if vote == 'n':
                node.right.setEffects(cause, self.causes[cause], tree[depth])
            self.DecisionTree(cause, tree, temp, node.right, depth+1, vote)

    def DecisionTreePartTwo(self, cause, tree, temp, node, depth, iList, training):
        if len(tree) == depth:
            node.path = temp
            #print node.leafDictionary, node.path
            return
        else:
            #retrun index of bestgain
            #print "gain", self.getGain(iList, training)
            vote = tree[depth]
            temp.append(vote)
            if vote == 'y':
                if node.left == None:
                    node.left = TreeNode(self.instances)
                node.left.setEffects(cause, self.causes[cause], 1)
                self.DecisionTreePartTwo(cause, tree, temp, node.left, depth+1, iList, training)

            elif vote == 'n':
                if node.right == None:
                    node.right = TreeNode(self.instances)
                node.right.setEffects(cause, self.causes[cause], 1)
                self.DecisionTreePartTwo(cause, tree, temp, node.right, depth+1, iList, training)

    def getGain(self, indexList, training):
        bestGain = [0.0, 0]
        for index in indexList:
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

            b = self.bEntropy(float(demY) / (demY + demN))
            r = self.remainder(demY, demN, repY, repN)
            gain = b - r

            if gain == 1.0:
                bestGain = [gain, index]
                break
            if gain > bestGain[0]:
                bestGain = [gain, index]

        return bestGain[1]

    def bEntropy(self, q):
        return -1 * (self.logEntropy(q) + self.logEntropy(1 - q))

    def logEntropy(self, q):
        if q == 0.0:
            return 0
        return q * math.log(q)

    def remainder(self, demY, repY, demN, repN):
        dem = demY + demN
        rep = repY + repN
        Y = float(demY + repY)
        Y = (Y / (dem + rep)) * self.bEntropy(demY / Y)
        N = float(demN + repN)
        N = (N / (dem + rep)) * self.bEntropy(demN / N)
        return Y + N

    def fillTree(self, depth, temp, node):
        #fills empty nodes and zeroes
        self.count += 1
        if depth == self.instances:
            temp = []
            return
        
        else:
            if node.left == None:
                node.left = TreeNode(self.instances)
                if depth+1 == self.depth:
                    temp.append('y')
                    node.left.path.extend(temp)
                    temp.pop()
            temp.append('y')
            self.fillTree(depth+1, temp, node.left)
            temp.pop()

            if node.right == None:
                node.right = TreeNode(self.instances)
                if depth+1 == self.depth:
                    temp.append('n')
                    node.right.path.extend(temp)
                    temp.pop()
            temp.append('n')
            self.fillTree(depth+1, temp, node.right)
            temp.pop()

    def initializeTestData(self, test):
        fTest = open(test)
        for line in fTest.readlines():
            line = line.strip('\n').split(',')
            tempDict = self.dict
            self.testInDecisionTree(line, self.root, tempDict, 0)
        fTest.close()

    def testInDecisionTree(self, tree, node, dict, depth):
        #keeping it here so as to count the last one
        if self.myAlgorithm == True:
            for keys in dict.iterkeys():
                dict[keys] += node.leafDictionary[keys]
        
        #predicting probabilities
        if len(tree) == depth:
            if self.myAlgorithm == False:
                for keys in node.leafDictionary.iterkeys():
                    dict[keys] = node.leafDictionary[keys]
            temp = dict.values()
            tempK = dict.keys()
            #print list(dict.items()), tree
            if temp[0] == temp[1]:
                print "republican" + "," + str(0.5)
            else:
                print str(tempK[temp.index(max(temp))]) + "," + str(max(temp)/sum(temp))
            #empty dict
            for keys in dict.iterkeys():
                dict[keys] = 0

        else:
            vote = tree[depth]
            if vote == 'y':
                self.testInDecisionTree(tree, node.left, dict, depth+1)
            else:
                self.testInDecisionTree(tree, node.right, dict, depth+1)
        
if __name__ == '__main__':
    training = 'Tests\\3.data'
    test = 'Tests\\3.test'
    D = DecisionTree()
    D.myAlgorithm = False
    D.inputData(training)
    D.inputTest(training)
    D.initiateDecisionTree(training)
    D.initializeTestData(test)