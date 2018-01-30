from __future__ import print_function
import os
import sys
import argparse
import math
import random
import csv

Ro  = [0.25+(i*0.1) for i in xrange(8)]
RoK =[0.5+(i*0.1) for i in xrange(10)]

class packet:

    def __init__(self,arrivalTime,packetSize,serviceTime=0,new_dpTime=0):
        self.arrivalTime = arrivalTime
        self.packetSize = packetSize
        self.serviceTime = serviceTime
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

def generateObserverList(T,Alpha):
    arrivalTime = nextTime(Alpha) #generate an arrival time
    newObserver = observer(arrivalTime) # create a observer for the new arrival time
    observerList = [newObserver]
    while(arrivalTime < T): # check if this arrival is still in the time period
        nextarrival = nextTime(Alpha) #generate an arrival time
        arrivalTime += nextarrival #increment the time counter
        newObserver = observer(arrivalTime) # create a observer for the new arrival time
        observerList += [newObserver] #add the new observer to the observer list
    return observerList

def generatePacketList(T,Lambda):
    arrivalTime = nextTime(Lambda) #generate an arrival time
    packetSize = nextTime(1.0/12000.0) #generate a random packet size
    serviceTime = packetSize/1000000 #calculate the service time
    departureTime = arrivalTime+serviceTime #calculate the departure time
    sojournTime  = departureTime - arrivalTime # calculate the sojourn time
    sojournList = [sojournTime]
    newPacket = packet(arrivalTime,packetSize,serviceTime,departureTime)
    packetList = [newPacket] #add the new packet to the packet list
    while(arrivalTime < T):# check if this arrival is still in the time period
        nextarrival = nextTime(Lambda)
        arrivalTime += nextarrival
        packetSize = nextTime(1.0/12000.0)
        serviceTime = packetSize/1000000
        if(arrivalTime >= packetList[-1].departureTime):
            #check if the queue is empty 
            departureTime = departureTime = arrivalTime+serviceTime
        else:
            #calculated the departure time base on the last packet departure time
            departureTime = packetList[-1].departureTime + serviceTime
        sojournTime  = departureTime - arrivalTime
        sojournList += [sojournTime]
        newPacket = packet(arrivalTime,packetSize,serviceTime,departureTime)
        packetList += [newPacket]
    resultList = [packetList,sojournList]
    return resultList

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
            packetCount = NofArrival-NofDeparture
            if(packetCount>0):
                packetCount = packetCount
            packetInQueueCount.append(packetCount)
            if(packetCount == 0):
                NofIdle = NofIdle + 1
    return [NofArrival,NofDeparture,NofObservation,NofIdle,packetInQueueCount]

def saveAs(fileName, data):
    with open("%s.csv" % fileName, "wb") as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerows(data)

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
    lastDpIndex = 0
    while(eventList):
        i = eventList[0]
        if(i.type == "Arrival"):
            packetSize = nextTime(1.0/12000.0)
            serviceTime = packetSize/1000000
            if (NofPacketInQueue < K+1):
                if(NofPacketInQueue == 0):
                    departureTime = i.time + serviceTime
                    mostRecentDpartTime = departureTime
                else:
                    departureTime = mostRecentDpartTime + serviceTime
                    mostRecentDpartTime = departureTime
                departureEvent = event("Departure",departureTime)
                resultList = departureInsert(eventList,departureEvent,lastDpIndex)
                lastDpIndex = resultList[1]
                eventList = resultList[0]
                NofArrival = NofArrival+1
                NofPacketInQueue = NofPacketInQueue + 1
            else:
                NofDropPacket = NofDropPacket + 1
        elif(i.type == "Departure"):
            NofDeparture = NofDeparture+1
            NofPacketInQueue = NofPacketInQueue -1
        else:
            NofObservation = NofObservation + 1
            packetCount = NofPacketInQueue
            packetInQueueCount.append(packetCount)
            if(packetCount == 1):
                NofIdle = NofIdle + 1
        eventList.pop(0)
        if(lastDpIndex > 0):
            lastDpIndex = lastDpIndex - 1

    return [NofArrival,NofDeparture,NofObservation,NofIdle,NofDropPacket,packetInQueueCount]


def departureInsert(eventList,departureEvent,dpIndex):
    i = dpIndex
    if(not eventList):
        return

    while(eventList[i].time < departureEvent.time):
        #print("eventLength: "+ str(len(eventList))+ "i length = "+ str(i) + " Type: " + eventList[i].type + " T1: "+ str(eventList[i].time)+ " T2 :" +str(departureEvent.time))
        j = len(eventList) -1
        if(len(eventList) == 1):
            break

        if(len(eventList)-i == 1):
            break
        i = i + 1
    eventList.insert(i+1,departureEvent)
    result = [eventList,i+1]
    return result

def checkMeanVariance(Lambda):
    randomTime = [nextTime(Lambda) for i in xrange(1000)]
    mean = sum(randomTime) / 1000
    variance = [x-mean for x in randomTime];
    variance = sum([x*x for x in variance])/1000
    expectedMean = 1/Lambda
    expectedVariance = expectedMean/Lambda
    print("Mean:" + str(mean) + " compare to " + str(expectedMean)+ "\n" + "Variance:" + str(variance)+ " compare to " + str(expectedVariance))

def infiniteBuffer():
    for r in Ro:
        la = calculateLambda(r)
        checkMeanVariance(la)
        print(la)
        packetsList = generatePacketList(1000,la)
        sojournList = packetsList[1]
        packetsList = packetsList[0]
        timeLength = len(sojournList)
        sojournTime = sum(sojournList)/timeLength
        observerList = generateObserverList(1000,la*2)
        print("starting")
        eventList = createDES(packetsList,observerList)
        print("sorting")
        eventList = mergeSort(eventList)
        print(len(eventList))
        result = eventHandler(eventList)
        E = float(sum(result[4]))
        L = float(len(result[4]))
        print(sum(result[4]))
        print(len(observerList))
        meanOfPacket = E/L
        Pidle = result[3]/L*100
        print("Average number of packets " + str(meanOfPacket))
        print("Average sojourn time "+str(sojournTime))
        print("The proportion of time the server is idle "+str(Pidle))
        print("NofArrival: " + str(result[0])+ " NofDeparture: "+str(result[1])+ " NofObservation: "+str(result[2])+ " NofIdle: "+ str(result[3])+"\n")


def finiteBuffer(K):
    la = calculateLambda(0.5)
    checkMeanVariance(la)
    print(la)
    packetsList = generatePacketListLimitK(1000,la)
    packetListSize = len(packetsList)*1.0
    observerList = generateObserverList(1000,la*2)
    print("starting")
    eventList = createDESK(packetsList,observerList)
    print("sorting")
    eventList = mergeSort(eventList)
    result = eventHandlerLimitK(eventList,K)
    E = float(sum(result[5]))
    L = float(len(result[5]))
    print(sum(result[5]))
    meanOfPacket = E/L
    Pidle = result[3]/L*100
    print("Average number of packets " + str(meanOfPacket))
    print("The proportion of time the server is idle "+str(Pidle))
    packetLoss = result[4]/packetListSize*100
    print("The percentage of packet loss "+str(packetLoss))
    print("NofArrival: " + str(result[0])+ " NofDeparture: "+str(result[1])+ " NofObservation: "+str(result[2])+ " NofIdle: "+ str(result[3])+ " NofPacketLoss: "+ str(result[4]))
    print(len(packetsList))
    print(len(observerList))


def main():
    infiniteBuffer()
    K = 5
    #finiteBuffer(K)

    #checkMeanVariance(75.0)


if __name__ == '__main__':
    main()
