from __future__ import print_function
import os
import sys
import argparse
import math
import random

Ro  = [0.25+(i*0.1) for i in xrange(8)]

class packet:
    def __init__(self,arrivalTime,packetSize,serviceTime):
        self.arrivalTime = arrivalTime
        self.packetSize = packetSize
        self.serviceTime = serviceTime

    def set_arrivalTime(self,new_arrivalTime):
        self.arrivalTime = new_arrivalTime

    def set_packetSize(self, new_size):
        self.packetSize = new_size

    def set_serviceime(self, new_serviceTime):
        self.serviceTime = new_serviceTime

    def set_departureTime(self, new_dpTime):
        self.departureTime = new_dpTime

class observer:
    def __init__(self,new_observeTime):
        self.observeTime = new_observeTime

def nextTime(rateParameter):
    return -math.log(1.0 - random.random()) / rateParameter

def calculateLambda(Ro):
    return Ro*1000000/12000

def generateObserverList(T,Lambda):
    arrivalTime = nextTime(Lambda)
    newObserver = observer(arrivalTime)
    observerList = [newObserver]
    while(arrivalTime < T):
        nextarrival = nextTime(Lambda)
        arrivalTime += nextarrival
        newObserver = observer(arrivalTime)
        observerList += [newObserver]
    return observerList

def generatePacketList(T,Lambda):
    arrivalTime = nextTime(Lambda)
    packetSize = nextTime(1.0/12000.0)
    serviceTime = packetSize/1000000
    newPacket = packet(arrivalTime,packetSize,serviceTime)
    packetList = [newPacket]
    while(arrivalTime < T):
        nextarrival = nextTime(Lambda)
        arrivalTime += nextarrival
        packetSize = nextTime(1.0/12000.0)
        serviceTime = packetSize/1000000
        newPacket = packet(arrivalTime,packetSize,serviceTime)
        packetList += [newPacket]
    return packetList

def checkMeanVariance(Lambda):
    randomTime = [nextTime(Lambda) for i in xrange(1000)]
    mean = sum(randomTime) / 1000
    variance = [x-mean for x in randomTime];
    variance = sum([x*x for x in variance])/1000
    expectedMean = 1/Lambda
    expectedVariance = expectedMean/Lambda
    print("Mean:" + str(mean) + " compare to " + str(expectedMean)+ "\n" + "Variance:" + str(variance)+ " compare to " + str(expectedVariance))

def main():
    la = calculateLambda(Ro[0])
    checkMeanVariance(la)
    print(la)
    packetsList = generatePacketList(10000,la)
    observerList = generateObserverList(10000,la*2)
    #print(str(packetsList[10000].serviceTime) +" "+ str(packetsList[10000].packetSize)) ##check packet generation





if __name__ == '__main__':
    main()
