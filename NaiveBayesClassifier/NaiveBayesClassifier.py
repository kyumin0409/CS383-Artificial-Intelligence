from pprint import pprint
import math

class CauseNode():
    def __init__(self, name, instances):
        self.count = 0
        self.cause = name
        self.instances = instances
        self.effects = {}
        self.initializeEffects()

    def initializeEffects(self):
        for effect in range(self.instances):
            self.effects[(effect, 'y')] = float(0)
            self.effects[(effect, 'n')] = float(0)

    def setEffects(self, key):
        # you count at total count because it's at a loc in line
        if self.effects.has_key(key):
            self.effects[key] += float(1) / (self.count)

    def fillZeroes(self):
        #this total value can change the accuracy of the output
        total = self.count * 1.25
        for effect in range(self.instances):
            if self.effects[(effect, 'y')] == 0.0:
                self.effects[(effect, 'y')] = float(1) / total
            if self.effects[(effect, 'n')] == 0.0:
                self.effects[(effect, 'n')] = float(1) / total

class NaiveBayesClassifier():
    def __init__(self):
        self.total = 0
        self.file = None
        self.queryList = []
        self.posteriorList = []
        self.causes = {}
        self.posterior = {}

    def inputData(self, file):
        #count ditribution of classes
        self.file = open(file)
        for lines in self.file.readlines():
            self.total += 1
            lines = lines.split(',')
            if not self.causes.has_key(lines[0]):
                self.causes[lines[0]] = CauseNode(lines[0], len(lines[1:]))
            self.causes[lines[0]].count += 1
            #initialize the effects
            self.causes[lines[0]].initializeEffects() 
        self.file.close()

        #adding effect values
        self.file = open(file)
        for lines in self.file.readlines():
            line = lines.strip('\n').split(',')
            cause = self.causes[line[0]]
            for effect in range(len(line[1:])):
                if line[1:][effect] != '?':
                    cause.setEffects((effect, line[1:][effect]))

        self.file.close()
        #filling zeroes
        for items in self.causes.itervalues():
            items.fillZeroes()

    def inputTest(self, file):
        self.file = open(file)
        for lines in self.file.readlines():
            line = lines.strip('\n').split(',')
            self.queryList.append(line)

    def NaiveBayesClassifier(self):
        log = True
        #with log
        if log == True:
            for qList in self.queryList:
                for key, value in self.causes.iteritems():
                    #P(Class)
                    probability = math.log(float(self.causes[key].count)) - math.log(self.total)
                    for index in range(len(qList)):
                        #SigmaP(Xi|Class)
                        if qList[index] == 'y' or qList[index] == 'n':
                            effectVal = float(self.causes[key].effects[index , qList[index]])
                            probability += math.log(effectVal)
                    self.posterior[key] = probability
                #calculating probs
                #add higher prob to querList
                if self.posterior['democrat'] == self.posterior['republican']:
                    self.posteriorList.append(['republican',0.5])
                else:
                    sumValues = sum(self.posterior.itervalues())
                    for cVar in self.posterior.iterkeys():
                        value = self.posterior[cVar] - sumValues
                        self.posterior[cVar] = math.exp(value)
                    maxValue = max(self.posterior.itervalues())
                    for k, v in self.posterior.iteritems():
                        if v == maxValue:
                            self.posteriorList.append([k, (v / sum(self.posterior.values())) ])

        #without log
        elif log == False:
            #calc NBC for each line and append it to pList
            for qList in self.queryList:
                for key, value in self.causes.iteritems():
                    probability = float(self.causes[key].count) / self.total
                    for index in range(len(qList)):
                        if qList[index] == 'y' or qList[index] == 'n':
                            probability *= float(self.causes[key].effects[index , qList[index]])
                    self.posterior[key] = probability
                #calculating probs
                #add higher prob to querList
                if self.posterior['democrat'] == self.posterior['republican']:
                    self.posteriorList.append(['republican',0.5])
                else:
                    sumValues = sum(self.posterior.itervalues())
                    for cVar in self.posterior.iterkeys():
                        value = self.posterior[cVar] / sumValues
                        self.posterior[cVar] = value
                    maxValue = max(self.posterior.itervalues())
                    #print maxValue
                    for k, v in self.posterior.iteritems():
                        if v == maxValue:
                            self.posteriorList.append([k,v])

    def printAnswer(self):
        for items in self.posteriorList:
            print str(items[0]) + "," + str(items[1])

if __name__ == '__main__':
    B = NaiveBayesClassifier()
    #B.inputData('house-votes-84.data')
    B.inputData('training.txt')
    B.inputTest('test.txt')
    B.NaiveBayesClassifier()
    B.printAnswer()