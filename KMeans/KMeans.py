import sys
import math
import copy
import random
import numpy as np

class KMeans():
    def __init__(self):
        self.clusters = 1
        self.data = []
        self.kDictionary = {}
        self.answer = []

    def input(self, file):
        f = open(file)
        for lines in f.readlines():
            lines = lines.strip('\n').split(' ')
            for index in range(1, len(lines)):
                lines[index] = float(lines[index])
            self.data.append(tuple(lines[1:]))
        self.buildCentroids()

    def buildCentroids(self):
        rand = False
        #this might coincide
        #random from dataset
        if rand == True:
            cData = copy.deepcopy(self.data)
            for index in range(self.clusters):
                r = random.choice(range(len(cData)))
                centroid = tuple(cData[r])
                cData.pop(r)
                self.kDictionary[centroid] = []

        #not random it should be first k examples
        else:
            for index in range(self.clusters):
                r = self.data[index]
                self.kDictionary[r] = []

    def Kmeans(self):
        #for all the data items
        #each item going through all the clusters
        for iterations in range(10): #iterations
            for item in self.data:
                minDict = {}
                for k, v in self.kDictionary.iteritems():
                    minDict[k] = self.euclideanDistance(k, item)

                #find the shortest dicstance out of all clusters
                mindistance = min(minDict.values())
                for key, val in minDict.iteritems():
                    if val == mindistance:
                        cluster = key
                        break
                
                #update cluster with mean
                #for one dimension
                mean = self.findMean(item, cluster)
                if self.kDictionary.has_key(mean) == False:
                    self.kDictionary[mean] = []
                    self.kDictionary.pop(cluster)
        
        #centroids stabilized, add values
        for items in self.data:
            minVal = 1.0
            for keys in self.kDictionary.iterkeys():
                mindistance = self.euclideanDistance(keys, items)
                if mindistance < minVal:
                    minVal = mindistance
                    minKey = keys
            self.kDictionary[minKey].append(items)

    def euclideanDistance(self, p, q):
        sum = 0.0
        for index in range(len(p)):
            sum += math.pow((p[index] - q[index]), 2)

        return math.sqrt(sum)

    def findMean(self, first, second):
        mean = []
        for i in range(len(first)):
            mean.append(None)

        for index in range(len(first)):
            mean[index] = (first[index] + second[index]) / 2
        return tuple(mean)

    def printClusters(self):
        #replicate centroids from main dict
        clusters = self.kDictionary.keys()
        self.answer = range(self.clusters)

        for index in self.data:
            for k, v in self.kDictionary.iteritems():
                if v.count(index) > 0:
                    print self.answer[clusters.index(k)]

    def plotScatter(self):
        #clusters
        colors = ['red', 'green', 'blue', 'black', 'yellow', 'brown', 'purple', 'pink', 'orange', 'magenta']
        cluster = self.kDictionary.keys()
        self.answer = range(self.clusters)
        
        for sublist in self.data:
            if len(sublist) == 1:
                length = len(sublist)
            else:
                length = len(sublist) - 1

            for index in range(length):
                for k, v in self.kDictionary.iteritems():
                    if v.count(sublist) > 0:
                        plot.scatter(sublist[index], sublist[index + 1], color=colors[cluster.index(k)], s=100, alpha=0.5)

        #Centroid cluster
        for index in range(len(cluster)):
            for item in range(len(cluster[index]) - 1):
                plot.scatter(cluster[index][item], cluster[index][item+1], color=colors[index], marker='^', s=100, alpha=1)

        plot.show()

if __name__ == '__main__':
    K = KMeans()
    K.clusters = 4
    K.input('test/1.data')
    K.Kmeans()
    K.printClusters()
    #K.plotScatter()