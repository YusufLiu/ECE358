from __future__ import print_function
import os
import sys
import argparse
import math
import random
import csv
import gc


BER =  [0,0.00001,0.0001]
tor = [0.005,0.25]
ratio = [2.5,5,7.5,10,12.5]
timeOutList5ms = []
timeOutList250ms = []
for i in ratio:
    timeOutList5ms.append(i*tor[0])

for i in ratio:
    timeOutList250ms.append(i*tor[1])

totalpacket= 0
next_expected_ack_Receiver = 0
H=54*8
current_time = 0
timeoutError = 0
C=5000000

class Event:
    def __init__(self,itype,time,error_flag,sequence_number):
        self.type= itype
        self.time = time
        self.error_flag = error_flag
        self.sequence_number = sequence_number

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

def ABPsender(H,l,C,timeOut,tor,BER):
    # initialization
    ES = []
    SN = 0
    next_expected_ack =(SN+1)%2
    global current_time
    current_time = 0
    packetLength = H+l
    totalSend = 1

    global totalpacket
    global next_expected_ack_Receiver
    totalpacket= 0
    next_expected_ack_Receiver = 0
    timeoutCounter = 0
    # H is header length, l is packet length
    current_time = current_time+packetLength/C
    TimeOutEvent = current_time+timeOut
    ES = addTimeOutEvent(ES,TimeOutEvent,SN)
    result = send(current_time,SN,packetLength,BER,tor)
    current_time = result.time+H/C
    #print(result.type)
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    #print("shoule be 2: " + str(len(ES)))
    while(totalpacket<1000):
        i = ES[0]
        #print(i.type)
        #print("current loop number:" + str(test))
        if(i.type == 'TimeOutEvent'):
            #print(len(ES))
            #print("process time out")
            timeoutCounter = timeoutCounter + 1
            TimeOutEvent = current_time+packetLength/C+timeOut
            ES = clearTimeOutEvent(ES)
            ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
            current_time = i.time+packetLength/C
            result = send(current_time,i.sequence_number,packetLength,BER,tor)
            totalSend = totalSend+1
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            #print(len(ES))
        elif (i.type == 'ACKEvent'):
            #print("process ack")
            #packet send and received correctly
            if(i.error_flag == 0 and next_expected_ack == i.sequence_number):
                if(SN<1):
                    SN = SN + 1
                else:
                    SN = 0
                next_expected_ack =(SN+1)%2
                ES = clearTimeOutEvent(ES)
                current_time = i.time+packetLength/C
                TimeOutEvent = current_time+timeOut
                ES = addTimeOutEvent(ES,TimeOutEvent,SN)
                result = send(current_time,SN,packetLength,BER,tor)
                totalSend = totalSend+1
                if(result.type != 'NIL'):
                    ES.append(result)
                    ES = mergeSort(ES)
            ES.remove(i)
    print("TimeOutCounter:" + str(timeoutCounter)    )
    return totalSend


def ABPsenderNACK(H,l,C,timeOut,tor,BER):
    # initialization
    ES = []
    SN = 0
    next_expected_ack =(SN+1)%2
    global current_time
    current_time = 0
    packetLength = H+l
    totalSend = 1

    global totalpacket
    global next_expected_ack_Receiver
    totalpacket= 0
    next_expected_ack_Receiver = 0
    timeoutCounter = 0
    # H is header length, l is packet length
    current_time = current_time+packetLength/C
    TimeOutEvent = current_time+timeOut
    ES = addTimeOutEvent(ES,TimeOutEvent,SN)
    result = send(current_time,SN,packetLength,BER,tor)
    current_time = result.time+H/C
    #print(result.type)
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    #print("shoule be 2: " + str(len(ES)))
    while(totalpacket<1000):
        i = ES[0]
        #print(i.type)
        #print("current loop number:" + str(test))
        if(i.type == 'TimeOutEvent'):
            #print(len(ES))
            #print("process time out")
            timeoutCounter = timeoutCounter + 1
            TimeOutEvent = current_time+packetLength/C+timeOut
            ES = clearTimeOutEvent(ES)
            ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
            current_time = i.time+packetLength/C
            result = send(current_time,i.sequence_number,packetLength,BER,tor)
            totalSend = totalSend+1
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            #print(len(ES))
        elif (i.type == 'ACKEvent'):
            #print("process ack")
            #packet send and received correctly
            if(i.error_flag == 0 and next_expected_ack == i.sequence_number):
                if(SN<1):
                    SN = SN + 1
                else:
                    SN = 0
                next_expected_ack =(SN+1)%2
                ES = clearTimeOutEvent(ES)
                current_time = i.time+packetLength/C
                TimeOutEvent = current_time+timeOut
                ES = addTimeOutEvent(ES,TimeOutEvent,SN)
                result = send(current_time,SN,packetLength,BER,tor)
                totalSend = totalSend+1
                if(result.type != 'NIL'):
                    ES.append(result)
                    ES = mergeSort(ES)
            elif(i.error_flag == 1 or next_expected_ack != i.sequence_number):
                ES = clearTimeOutEvent(ES)
                current_time = i.time+packetLength/C
                TimeOutEvent = current_time+timeOut
                ES = addTimeOutEvent(ES,TimeOutEvent,SN)
                result = send(current_time,SN,packetLength,BER,tor)
                totalSend = totalSend+1
                if(result.type != 'NIL'):
                    ES.append(result)
                    ES = mergeSort(ES)
            ES.remove(i)

    print("TimeOutCounter:" + str(timeoutCounter)    )
    return totalSend


def GBNsenderOld(H,l,C,timeOut,N):
    ES = []
    M = []
    SN = []
    L = []
    T = []
    global current_time
    current_time = 0
    packetLength = H+l
    totalPacket = 1
    global totalpacket
    global next_expected_ack_Receiver
    next_expected_ack_Receiver = 0
    timeoutCounter = 0
    SN[1] = 0
    L[1] = H+l
    T[1] = current_time + L[1]/C
    M[0] = [SN[1],L[1],T[1]]
    for i in range(2,N):
        SN[i] = SN([i-1] +1)%(N+1)
        L[i] = H + l
        T[i] = T[i-1] + L[i]/C
        M[i-1] = [SN[i],L[i],T[1]]
    p = 0
    TimeOutTime=timeOut
    TimeOutEvent = M[p][2] +TimeOutTime
    ES = addTimeOutEvent(ES,TimeOutEvent,M[p][0])
    p=p+1
    result = sendGBN(SN,packetLength,current_time)
    current_time = current_time+packetLength/C
    TimeOutEvent = current_time+timeOut
    ES = addTimeOutEvent(ES,TimeOutEvent,SN)
    result = sendGBN(current_time,SN,packetLength,BER,tor)
    current_time = result.time+H/C
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    while(ES):
        i = ES[0]
        while(current_time<i.time):
            ES = addTimeOutEvent(ES,TimeOutEvent,M[p][0])
            result = sendGBN(M[p][0],packetLength,current_time)
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            current_time = current_time +  M[p][1]
            p = (p+1)%N

        ES.remove(i)
        if(i.type == 'TimeOutEvent'):
            TimeOutEvent = current_time+packetLength/C+TimeOutTime
            ES = addTimeOutEvent(ES,TimeOutEvent,SN)
            result = send(SN,packetLength,current_time)
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
        elif (i.type == 'ACKEvent'):
            #packet send and received correctly
            if(i.error_flag == 0 and next_expected_ack == i.sequence_number):
                if(SN<2):
                    SN = SN + 1
                else:
                    SN = 0
                next_expected_ack =(SN+1)%2
                ES = clearTimeOutEvent(ES)
                TimeOutEvent = current_time+packetLength/C+TimeOutTime
                ES = addTimeOutEvent(ES,TimeOutEvent,SN)
                result = send(SN,packetLength,current_time)
                if(result.type != 'NIL'):
                    ES.append(result)
                    ES = mergeSort(ES)


    packetLength = H+l

def GBNsender(H,l,C,timeOut,tor,BER):
    # initialization
    ES = []
    SN = []
    L = []
    T = []
    M = []
    SN = 0
    next_expected_ack =(SN+1)%2
    global current_time
    current_time = 0
    packetLength = H+l
    totalPacket = 1

    global totalpacket
    global next_expected_ack_Receiver
    totalpacket= 0
    next_expected_ack_Receiver = 0
    timeoutCounter = 0

    SN[1] = 0
    L[1] = packetLength

    T[1] = current_time + L[1]/C

    # H is header length, l is packet length
    current_time = current_time+packetLength/C
    TimeOutEvent = current_time+timeOut
    ES = addTimeOutEvent(ES,TimeOutEvent,SN)
    result = send(current_time,SN,packetLength,BER,tor)
    current_time = result.time+H/C
    #print(result.type)
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    #print("shoule be 2: " + str(len(ES)))
    while(totalpacket<100):
        i = ES[0]
        #print(i.type)
        #print("current loop number:" + str(test))
        if(i.type == 'TimeOutEvent'):
            #print(len(ES))
            #print("process time out")
            timeoutCounter = timeoutCounter + 1
            TimeOutEvent = current_time+packetLength/C+timeOut
            ES = clearTimeOutEvent(ES)
            ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
            current_time = i.time+packetLength/C
            result = send(current_time,i.sequence_number,packetLength,BER,tor)
            totalpacket = totalpacket+1
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            #print(len(ES))
        elif (i.type == 'ACKEvent'):
            #print("process ack")
            #packet send and received correctly
            if(i.error_flag == 0 and next_expected_ack == i.sequence_number):
                if(SN<1):
                    SN = SN + 1
                else:
                    SN = 0
                next_expected_ack =(SN+1)%2
                ES = clearTimeOutEvent(ES)
                current_time = i.time+packetLength/C
                TimeOutEvent = current_time+timeOut
                ES = addTimeOutEvent(ES,TimeOutEvent,SN)
                result = send(current_time,SN,packetLength,BER,tor)
                totalpacket = totalpacket+1
                if(result.type != 'NIL'):
                    ES.append(result)
                    ES = mergeSort(ES)
            ES.remove(i)
    print("TimeOutCounter:" + str(timeoutCounter)    )
    return totalpacket



def clearTimeOutEvent(ES):
    for i in ES:
        if(i.type == 'TimeOutEvent'):
            ES.remove(i)

    return ES



def addTimeOutEvent(ES,time,SN):
    TimeOutEvent = Event('TimeOutEvent',time,0,SN)
    ES.append(TimeOutEvent)
    return mergeSort(ES)

def send(Time,SN,packetLength,BER,tor):
    #print('SN#'+str(SN))
    #print("going to forward channel")
    #print('SN#'+str(SN))
    global timeoutError
    resend = 0
    result = Channel(Time,SN,packetLength,BER,tor) # sender to recevier
    #print("going to recevier")
    if(result[1] == 'NIL'):
        resend = 1
        #print('packetloss')
    if(timeoutError ==1):
        resend = 1
        timeoutError = 0

    result = ABPreceiver(result[0],result[1],result[2])
    #print("going to reversal channel")
    result = Channel(result[0],result[1],result[2],BER,tor)# receiver to sender
    #print('SN#'+str(result[1]))
    if(timeoutError ==1):
        timeoutError = 0
        return Event('ACKEvent',result[0],1,result[2])

    if(resend == 1):
        return Event('NIL',result[0],1,result[2])

    if(result[1] == 'NIL'):
        #print('ack loss')
        return Event('NIL',result[0],1,result[2])
    else:
        #print('SN:'+str(SN))
        #print('ACKtime:'+str(result[0]))
        return Event('ACKEvent',result[0],result[1],result[2])

def sendGBN(Time,SN,packetLength):
    ploss = 0.2
    propDelay = 0.1
    result = Channel(Time,SN,packetLength) # sender to recevier
    result = ABPreceiver(result[0],result[1],result[2])
    result = Channel(result[0],result[1],result[2])# receiver to sender
    if(result[1] == 'NIL'):
        return Event('NIL',result[0],1,result[2])
    else:
        return Event('ACKEvent',result[0],result[1],result[2])

def Channel(Time,SN,packetLength,BER,tor):
    i = 0
    result = []
    global timeoutError
    status = ''
    while(i < packetLength):
        i= i +1
        result.append(generate01(BER))
    errorCount = 0
    for i in result:
        if(i==0):
            errorCount = errorCount+1
    #print('errorCount:'+str(errorCount))
    if(errorCount == 0):
        return [Time+tor,0,SN]
    elif(errorCount < 5):
        #print('error')
        timeoutError=1
        return [Time+tor,1,SN]
    else:
        #print("Oh NO")
        return [Time+tor,'NIL',SN]


def ABPreceiver(Time,Status,SN):
    global totalpacket
    global next_expected_ack_Receiver
    #print('current'+str(next_expected_ack_Receiver))
    #print('SN:'+str(SN))
    #print('recievetime:'+str(Time))
    global current_time
    current_time = Time+H/C
    if(Status == 0 and next_expected_ack_Receiver == SN):
        totalpacket = totalpacket+1
        next_expected_ack_Receiver = (next_expected_ack_Receiver+1)%2
    return [current_time,next_expected_ack_Receiver,H]

def generate01(BER):
    number = random.random()
    if(number <= BER):
        return 0
    else:
        return 1



def main():
    #ABP
    global totalpacket
    for i in timeOutList5ms:
        for z in BER:
            totalsend = ABPsender(H,1500*8,C,i,tor[0],z)
            print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    for i in timeOutList5ms:
        for z in BER:
            totalsend = ABPsender(H,1500*8,C,i,tor[1],z)
            print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    #ABP

if __name__ == '__main__':
    main()
