import copy
import math
import sys

def main(argv):
    points = getInput(argv[0])
    k = int(3)
    centers = []
    for i in range(k):
        points[i][0] = i
        centers.append(copy.copy(points[i]))
    for value in cluster(points, centers):
        print value[0]

def getInput(filename):
    '''
    Grabs input from argument, removes first index so as not to cheat
    '''
    input = open('1.test', 'r')
    points = []
    for line in input:
        line = line.split()
        line.pop(0)
        line = map(float, line)
        line.insert(0, 0)
        points.append(line)
    input.close()
    return points

def cluster(points, centers, iteration=0):
    '''
    Clusters based on euclidian distance
    If clustering does not change, then return clusters
    
    Cuts out at 1mil iterations
    '''
    if iteration == 1000: #1mil
        return points
    parentPoints = copy.copy(points)
    for point in points:
        shortestDist = 0
        for center in centers:
            distance = 0
            for i in range(1, len(center)):
                distance += math.pow((point[i] - center[i]),2)
            distance = math.sqrt(distance)
            if distance < shortestDist or type(shortestDist) == int:
                shortestDist = distance
                point[0] = center[0]
    noChange = True
    for i in range(len(points)):
        if points[i][0] != parentPoints[i][0]:
            noChange = False
    if noChange:
        return points
    for center in centers:
        for i in range(1, len(center)):
            center[i] = 0.0
        clusterPoints = [pt for pt in points if pt[0] == center[0]]
        for point in clusterPoints:
            for i in range(1, len(point)):
                center[i] += point[i]
        for i in range(1, len(center)):
            center[i] /= len(clusterPoints)
    cluster(points, centers, (iteration + 1))

if __name__ == '__main__':
    main('1.test')