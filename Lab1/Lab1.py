from __future__ import print_function
import os
import sys
import argparse
import math
import random

Ro  = [0.25+(i*0.1) for i in xrange(8)]
RoK =[0.5+(i*0.1) for i in xrange(10)]

class packet:

    def __init__(self,arrivalTime,packetSize,serviceTime=0,new_dpTime=0):
        self.arrivalTime = arrivalTime
        self.packetSize = packetSize
        self.serviceTime = serviceTime
        self.departureTime = new_dpTime

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

class event:
    def __init__(self,new_type,new_time):
        self.type = new_type
        self.time = new_time


def createDES(packetList,observerList):
    eventList = []
    for i in packetList:
        arrivalEvent = event("Arrival",i.arrivalTime)
        #print(arrivalEvent.type)
        eventList.append(arrivalEvent)
        departureEvent = event("Departure",i.departureTime)
        eventList.append(departureEvent)
    print("packetlist done")
    for i in observerList:
        observerEvent = event("Observer",i.observeTime)
        eventList.append(observerEvent)

    return eventList

def createDESK(packetList,observerList):
    eventList = []
    for i in packetList:
        arrivalEvent = event("Arrival",i.arrivalTime)
        #print(arrivalEvent.type)
        eventList.append(arrivalEvent)

    print("packetlist done")
    for i in observerList:
        observerEvent = event("Observer",i.observeTime)
        eventList.append(observerEvent)

    return eventList

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
    departureTime = arrivalTime+serviceTime
    newPacket = packet(arrivalTime,packetSize,serviceTime,departureTime)
    packetList = [newPacket]
    while(arrivalTime < T):
        nextarrival = nextTime(Lambda)
        arrivalTime += nextarrival
        packetSize = nextTime(1.0/12000.0)
        serviceTime = packetSize/1000000
        if(arrivalTime >= packetList[-1].departureTime):
            departureTime = departureTime = arrivalTime+serviceTime
        else:
            departureTime = packetList[-1].departureTime + serviceTime
        newPacket = packet(arrivalTime,packetSize,serviceTime,departureTime)
        packetList += [newPacket]
    return packetList

def generatePacketListLimitK(T,Lambda):
    arrivalTime = nextTime(Lambda)
    packetSize = nextTime(1.0/12000.0)
    newPacket = packet(arrivalTime,packetSize)
    packetList = [newPacket]
    while(arrivalTime < T):
        nextarrival = nextTime(Lambda)
        arrivalTime += nextarrival
        packetSize = nextTime(1.0/12000.0)
        newPacket = packet(arrivalTime,packetSize)
        packetList += [newPacket]
    return packetList

def mergeSort(alist):
    if len(alist)>1:
        mid = len(alist)//2
        lefthalf = alist[:mid]
        righthalf = alist[mid:]

        mergeSort(lefthalf)
        mergeSort(righthalf)

        i=0
        j=0
        k=0
        while i < len(lefthalf) and j < len(righthalf):
            if lefthalf[i].time < righthalf[j].time:
                alist[k]=lefthalf[i]
                i=i+1
            else:
                alist[k]=righthalf[j]
                j=j+1
            k=k+1

        while i < len(lefthalf):
            alist[k]=lefthalf[i]
            i=i+1
            k=k+1

        while j < len(righthalf):
            alist[k]=righthalf[j]
            j=j+1
            k=k+1
    return alist


def eventHandler(eventList):
    NofArrival = 0
    NofDeparture = 0
    NofObservation = 0
    NofIdle = 0
    packetInQueueCount = []
    for i in eventList:
        if(i.type == "Arrival"):
            NofArrival = NofArrival+1
        elif(i.type == "Departure"):
            NofDeparture = NofDeparture+1
        else:
            NofObservation = NofObservation + 1
            packetCount = NofArrival-NofDeparture-1
            packetInQueueCount.append(packetCount)
            if(packetCount == 0):
                NofIdle = NofIdle + 1

    return [NofArrival,NofDeparture,NofObservation,NofIdle,packetInQueueCount]

def eventHandlerLimitK(eventList,K):
    NofArrival = 0
    NofDeparture = 0
    NofObservation = 0
    NofIdle = 0
    NofDropPacket = 0
    NofPacketGenerate = 0
    packetInQueueCount = []
    NofPacketInQueue = 0
    mostRecentDpartTime = 0
    while(eventList):
        i = eventList[0]
        if(i.type == "Arrival"):
            packetSize = nextTime(1.0/12000.0)
            serviceTime = packetSize/1000000
            if (NofPacketInQueue <= K+1):
                if(NofPacketInQueue == 0):
                    departureTime = i.time + serviceTime
                    mostRecentDpartTime = departureTime
                else:
                    departureTime = mostRecentDpartTime + serviceTime
                    mostRecentDpartTime = departureTime
                departureEvent = event("Departure",departureTime)
                eventList = departureInsert(eventList,departureEvent)
                NofArrival = NofArrival+1
                NofPacketInQueue = NofPacketInQueue + 1
            else:
                NofDropPacket = NofDropPacket + 1
        elif(i.type == "Departure"):
            NofDeparture = NofDeparture+1
            NofPacketInQueue = NofPacketInQueue -1
        else:
            NofObservation = NofObservation + 1
            packetCount = NofPacketInQueue - 1
            packetInQueueCount.append(packetCount)
            if(packetCount == 1):
                NofIdle = NofIdle + 1
        eventList.pop(0)

    return [NofArrival,NofDeparture,NofObservation,NofIdle,NofDropPacket,packetInQueueCount]


def departureInsert(eventList,departureEvent):
    i = 0
    if(not eventList):
        return

    while(eventList[i].time < departureEvent.time):
        print("eventLength: "+ str(len(eventList))+ "i length = "+ str(i) + " Type: " + eventList[i].type + " T1: "+ str(eventList[i].time)+ " T2 :" +str(departureEvent.time))
        j = len(eventList) -1
        if(len(eventList) == 1):
            break
        i = i + 1
    #if(len(eventList) > 1):
    eventList.insert(i+1,departureEvent)
    return eventList

def checkMeanVariance(Lambda):
    randomTime = [nextTime(Lambda) for i in xrange(1000)]
    mean = sum(randomTime) / 1000
    variance = [x-mean for x in randomTime];
    variance = sum([x*x for x in variance])/1000
    expectedMean = 1/Lambda
    expectedVariance = expectedMean/Lambda
    print("Mean:" + str(mean) + " compare to " + str(expectedMean)+ "\n" + "Variance:" + str(variance)+ " compare to " + str(expectedVariance))

def infiniteBuffer():
    la = calculateLambda(Ro[0])
    checkMeanVariance(la)
    print(la)
    packetsList = generatePacketList(10000,la)
    observerList = generateObserverList(10000,la*2)
    print("starting")
    eventList = createDES(packetsList,observerList)
    print("sorting")
    eventList = mergeSort(eventList)
    print(len(eventList))
    result = eventHandler(eventList)
    print("NofArrival: " + str(result[0])+ "NofDeparture: "+str(result[1])+ "NofObservation: "+str(result[2])+ "NofIdle: "+ str(result[3]))


def finiteBuffer(K):
    la = calculateLambda(RoK[0])
    checkMeanVariance(la)
    print(la)
    packetsList = generatePacketListLimitK(1000,la)
    observerList = generateObserverList(1000,la*2)
    print("starting")
    eventList = createDESK(packetsList,observerList)
    print("sorting")
    eventList = mergeSort(eventList)
    result = eventHandlerLimitK(eventList,K)
    print("NofArrival: " + str(result[0])+ " NofDeparture: "+str(result[1])+ " NofObservation: "+str(result[2])+ " NofIdle: "+ str(result[3]))
    print(len(packetsList))
    print(len(observerList))



def main():
    #infiniteBuffer()
    K = 5
    finiteBuffer(K)


if __name__ == '__main__':
    main()
