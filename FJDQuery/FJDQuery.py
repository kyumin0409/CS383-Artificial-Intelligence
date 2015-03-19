import sys
class FJDQuery():
    def __init__(self, file):
        self.file = file
        self.totalInstances = 1728
        self.probability = []
        self.probabilityList = []
        self.conditionalList = []
        self.lineList = []
        self.condList = []
        self.combinationList = []
        self.probabilityAnswer = {}
        self.conditionalAnswer = {}
        self.answerDict = {}
        self.indexList = ["buying", "maint", "door", "persons", "lug_boot", "safety", "car"]
        self.dictionary = {"car": {"unacc": 0 , "acc": 0 , "good": 0 , "vgood": 0 },
                           "buying" : {"vhigh": 0 , "high": 0 , "med": 0 , "low": 0 }, 
                           "maint" : {"vhigh": 0 , "high": 0 , "med": 0 , "low": 0 }, 
                           "doors" : {"2": 0 , "3": 0 , "4": 0 , "5more": 0 }, 
                           "persons" : {"2": 0 , "4": 0 , "more": 0 },
                           "lug_boot": {"small": 0 , "med": 0 , "big": 0 }, 
                           "safety": {"low": 0 , "med": 0 , "high": 0 }
                           }
  
    def constructFJD(self):
        #create a dictionary of keys that are list
        string = ""
        stringList = []
        file = open(self.file, 'r')
        for line in file.readlines():
            for char in line:
                if(char == ','):
                    stringList.append(string)
                    string = ""
                elif(char == '\n'):
                    stringList.append(string)
                    string = ""
                    break
                else:
                    string += char
            self.lineList.append(stringList)
            stringList = []
        #print self.lineList
        file.close()
        
    def inputQuery(self):
        #doing multiple things
        #file = open("test.txt", "r")
        user_input = [] 
        entry = raw_input("Enter text: press ENTER to exit \n") 
        while entry: 
            user_input.append(entry) 
            entry = raw_input("") 
        user_input = '\n'.join(user_input) 
        #print user_input
        f = open('text.txt', 'w')
        f.writelines(user_input)
        f.close()

        file = open('text.txt', 'r')
        firstLine = file.readline().split()
        self.probability.extend(firstLine)
        for line in file.readlines():
            secondLine = line.split()
            self.conditionalList.append((secondLine[0], secondLine[1:]))
        
    def constructCombinationList(self):

        #Probabilities
        #first probability
        for k in self.dictionary.get(self.probability[0]).iterkeys():
            self.combinationList.append([k])
        
        #For all the other probabilities
        if len(self.probability) > 1:
            #for each prob query [, maint]
            for i in range(1, len(self.probability)):
                prevLength = len(self.combinationList)
                #for each value in first list [low, med, high]
                for j in range(prevLength):
                    tempList = []
                    #for each values in that prob [vhigh, high, med, low]
                    for keys in self.dictionary.get(self.probability[i]).iterkeys():
                        #appending [low, vhigh], [low, high], ...
                        if type(self.combinationList[j]) == list:
                            temp = []
                            for items in self.combinationList[j]:
                                temp.append(items)
                            temp.append(keys)
                            tempList.append(temp)
                        else:
                            tempList.append([self.combinationList[j], keys])
                        #this loop is going to end
                    self.combinationList.extend(tempList)
                #clear the previous list for probabilities
                for x in range(prevLength):
                    self.combinationList.pop(0)
        self.probabilityList = self.combinationList
        
        #conditionals
        if len(self.conditionalList) > 0:
            List = []
            for fT in self.conditionalList[0][1]:
                List.append([fT])
            
            if len(self.conditionalList) > 1:
                for iX in range(1,len(self.conditionalList)):
                    length = len(List)
                    tempList = []
                    for jX in range(length):
                        items = self.conditionalList[iX][1]
                        for item in items:
                            temp = []
                            for it in List[jX]:
                                temp.append(it)
                            temp.append(item)
                            tempList.append(temp)
                    for X in range(length):
                        List.pop(0)
                    List.extend(tempList)
            #so i can access it in search query
            self.condList = List

            #constructing combinations of probs and conds
            tempCombinationList = []
            for items in List:
                for things in self.combinationList:
                    temp = []
                    temp.extend(things)
                    temp.extend(items)
                    tempCombinationList.append(temp)
            self.combinationList = tempCombinationList
            
    def searchQuery(self): 
        #make a list of corresponding indices
        tempDex = []
        tempDexConditional = []
        #print self.probabilityList
        for ix in self.probability:
            tempDex.append(self.indexList.index(ix))
        #print tempDex
        for jx in self.conditionalList:
            #test
            tempDex.append(self.indexList.index(jx[0]))
            tempDexConditional.append(self.indexList.index(jx[0]))
        #print tempDex


        for items in self.combinationList:
        #for items in self.probabilityList:
            #convert items to string
            tString = ""
            #prob + cond
            for it in items:
                tString += it + " "
            self.probabilityAnswer[tString] = 0
            #for each line in fileset data
            for line in self.lineList:
                counter = 0
                for index in range(len(items)):
                    if line[tempDex[index]] == items[index]:
                        counter += 1
                if counter == len(items):
                    self.probabilityAnswer[tString] += 1
                    #popping lines fucked the calculations
        
        #just conditional
        for item in self.condList:
            sString = ""
            for ti in item:
                sString += ti + " "
            self.conditionalAnswer[sString] = 0

            for line in self.lineList:
                counter = 0
                for index in range(len(item)):
                    if line[tempDexConditional[index]] == item[index]:
                        counter += 1
                if counter == len(item):
                    self.conditionalAnswer[sString] += 1

    def conditionalClause(self):
        #populating answer dict
        for items in self.probabilityList:
            tString = ""
            for item in items:
                tString += item + " "
            self.answerDict[tString] = 0
        
        for k, v in self.probabilityAnswer.iteritems():
            lis = k.split()
            for items in self.probabilityList:
                counter = 0
                for index in range(len(items)):
                    if lis[index] == items[index]:
                        counter += 1
                if counter == len(items):
                    tString = ""
                    for item in items:
                        tString += item + " "
                    self.answerDict[tString] += v
        
    def printAnswer(self):
        if len(self.conditionalList) == 0:
            for k, v in self.probabilityAnswer.iteritems():
                print k, float(self.probabilityAnswer[k]) / self.totalInstances
        else:
            self.conditionalClause()
            for key, val in self.answerDict.iteritems():
                print key, float(self.answerDict[key]) / sum(self.conditionalAnswer.itervalues())

if __name__== '__main__':
    Q = FJDQuery('car.data')
    Q.constructFJD()
    Q.inputQuery()
    Q.constructCombinationList()
    Q.searchQuery()
    Q.printAnswer()