from __future__ import print_function
import os
import sys
import argparse
import math
import random
import csv
import gc

N=4

BER =  [0,0.00001,0.0001]
tor = [0.005,0.25]
ratio = [2.5,5.0,7.5,10.0,12.5]
timeOutList5ms = []
timeOutList250ms = []
for i in ratio:
    timeOutList5ms.append(i*tor[0])

for i in ratio:
    timeOutList250ms.append(i*tor[1])

totalpacket= 0
next_expected_ack_Receiver = 0
H=54*8.0
current_time = 0
timeoutError = 0
C=5000000.0

p_GBN_Receiver = 0

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
            current_time = i.time+packetLength/C
            TimeOutEvent = current_time+timeOut
            ES = clearTimeOutEvent(ES)
            ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
            result = send(current_time,i.sequence_number,packetLength,BER,tor)
            totalSend = totalSend+1
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            #print(len(ES))
        elif (i.type == 'ACKEvent'):
            print("process ack")
            #packet send and received correctly
            print(current_time)
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
    current_time = current_time+tor
    return current_time


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
            current_time = i.time+packetLength/C
            TimeOutEvent = current_time+timeOut
            ES = clearTimeOutEvent(ES)
            ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
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




def GBNsender(H,l,C,timeOut,tor,BER):
    # initialization
    ES = []
    SN = []
    L = []
    T = []
    M = []

    global current_time
    current_time = 0
    packetLength = H+l
    totalPacket = 1
    global p_GBN_Receiver
    global totalpacket

    totalpacket= 0
    next_expected_ack_Receiver = 0
    timeoutCounter = 0

    SN.append(0)
    L.append(0)
    T.append(0)

    SN.append(0)
    L.append(packetLength)
    print(packetLength)
    T.append(current_time + packetLength/C)
    M.append([SN[1],L[1],T[1]])

    for i in range(2,N+1):
        SN.append((SN[i-1] +1)%(N+1))
        L.append(packetLength)
        T.append(T[i-1] + L[i]/C)
        M.append([SN[i],L[i],T[i]])

    print(M)
    p = 0
    #queueFull = 0
    packetInQ =0
    current_time = current_time+packetLength/C
    TimeOutEvent = current_time+timeOut
    ES = addTimeOutEvent(ES,TimeOutEvent,M[0][0])
    result = sendGBN(current_time,M[0][0],packetLength,BER,tor)
    packetInQ = packetInQ +1
    #print(result.type)
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    # H is header length, l is packet length
    while(packetInQ < 4):
        current_time = current_time+packetLength/C
        result = sendGBN(M[packetInQ][2],M[packetInQ][0],packetLength,BER,tor)
        packetInQ = packetInQ +1
        #print(result.type)
        if(result.type != 'NIL'):
            ES.append(result)
            ES = mergeSort(ES)

    current_time = M[packetInQ-1][2]
    print(current_time)
    print(len(ES))
    print('EVENT in ES')
    # for z in ES:
    #     print ('type:'+str(z.type)+' time:'+str(z.time)+' SN:'+str(z.sequence_number))
    #print("shoule be 2: " + str(len(ES)))
    while(totalpacket<1000):
        i = ES[0]
        print(i.type)



        # print('current_time: ' + str(current_time) + " event time: "+str(i.time))
        while(current_time<= i.time and packetInQ < 4):
            current_time = current_time+packetLength/C
            transTime = current_time
            result = sendGBN(transTime,M[packetInQ][0],packetLength,BER,tor)
            packetInQ = packetInQ +1
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
            current_time = transTime

        # print('current_time: ' + str(current_time) + " event time: "+str(i.time))

        # print('EVENT in ES')
        # for z in ES:
        #     print ('type:'+str(z.type)+' time:'+str(z.time)+' SN:'+str(z.sequence_number))

            #p = (p+1)%N
        #print("current loop number:" + str(test))
        if(i.type == 'TimeOutEvent'):
            #print(len(ES))
            #print("process time out")
            # print("process timeout time:" + str(i.time))
            # print("SN being processed:"+str(i.sequence_number))
            timeoutCounter = timeoutCounter + 1
            current_time = i.time+packetLength/C
            TimeOutEvent = current_time+timeOut
            ES = clearTimeOutEvent(ES)
            if(M[0][0] ==i.sequence_number):
                #ES = clearOtherACK(ES,i.sequence_number)
                ES= []
                ES = addTimeOutEvent(ES,TimeOutEvent,i.sequence_number)
            else:
                print("something wrong")
            M[0][2] = current_time
            for r in range(1,4):
                M[r][2] = M[r-1][2]+packetLength/C

            p_GBN_Receiver = i.sequence_number
            p=i.sequence_number
            result = sendGBN(current_time,i.sequence_number,packetLength,BER,tor)
            packetInQ=1


            if(result.type != 'NIL'):
                print("succusseful resend")
                ES.append(result)
                ES = mergeSort(ES)

            #print(len(ES))
        elif (i.type == 'ACKEvent'):
            # print("process ack time:" + str(i.time))
            # print("SN being processed:"+str(i.sequence_number))

            #packet send and received correctly
            acceptableRN = [(p+1)%5,(p+2)%5,(p+3)%5,(p+4)%5]
            # print('acceptableRN:' + str(acceptableRN))
            if(i.error_flag == 0 and  i.sequence_number in acceptableRN):
                slideSize = (i.sequence_number-p)%5
                ES = clearTimeOutEvent(ES)
                newQ = shiftAndFill(M,slideSize,i.time,SN,T,L)
                M = newQ[0]
                # print('New M:')
                # print(M)
                SN = newQ[1]
                T = newQ[2]
                p = M[0][0]
                packetInQ = 4-slideSize
                current_time = i.time
                TimeOutEvent = M[0][2]+timeOut
                ES = addTimeOutEvent(ES,TimeOutEvent,M[0][0])
                ES = mergeSort(ES)
                print(len(ES))
                # while(packetInQ<4 and M[packetInQ][2]< current_time):
                #     result = sendGBN(current_time,M[packetInQ][0],packetLength,BER,tor)
                #     packetInQ = packetInQ +1



            ES.remove(i)
    # print("TimeOutCounter:" + str(timeoutCounter)    )
    # print(current_time)
    return totalpacket


def clearOtherACK(ES,n):
    for f in ES:
        if(f.sequence_number == n):
            ES.remove(f)
    return ES

def shiftAndFill(M,slideSize,current_time,SN,T,L):
    print("shifting")
    SN= SN[slideSize:]
    L= L[slideSize:]
    T = T[slideSize:]
    M = M[slideSize:]
    # SN[1] = SN[slideSize+1]
    # L[1] = L[1]
    # T[1] = T[slideSize+1]
    # M[0] = [SN[1],L[1],T[1]]
    firstTrans = 0
    for i in range(len(M),4):
        SN.append((SN[i] +1)%(5))
        L.append(L[0])
        if(firstTrans == 0):
            T.append(current_time + L[i]/C)
            firstTrans =1
        else:
           T.append( T[i-1] + L[i]/C)
        M.append([SN[i+1],L[i+1],T[i+1]])

    # for i in range(2,5):
    #     SN[i] = (SN[i-1] +1)%(5)
    #     L[i] = L[1]
    #     T[i] = T[i-1] + L[i]/C
    #     M[i-1] = [SN[i],L[i],T[i]]

    return [M,SN,T]

def clearTimeOutEvent(ES):
    toRemove = []
    for i in ES:
        if(i.type == 'TimeOutEvent'):
            toRemove.append(i)
    for z in toRemove:
        ES.remove(z)
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

def sendGBN(Time,SN,packetLength,BER,tor):
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

    result = GBNreceiver(result[0],result[1],result[2])
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

def GBNreceiver(Time,Status,SN):
    global totalpacket
    global p_GBN_Receiver
    #print('current'+str(next_expected_ack_Receiver))
    #print('SN:'+str(SN))
    #print('recievetime:'+str(Time))
    print("received" + str(SN))
    global current_time
    current_time = Time+H/C
    if(Status == 0 and SN == p_GBN_Receiver):
        totalpacket = totalpacket+1
        p_GBN_Receiver = (p_GBN_Receiver+1)%5
    return [current_time,p_GBN_Receiver,H]

def generate01(BER):
    number = random.random()
    if(number <= BER):
        return 0
    else:
        return 1



def main():
    #ABP
    global totalpacket
    # print("ABP Simulation Results")
    # for i in timeOutList5ms:
    #     for z in BER:
    #         totalsend = ABPsender(H,1500.0*8,C,i,tor[0],z)
    #         print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    # for i in timeOutList5ms:
    #     for z in BER:
    #         totalsend = ABPsender(H,1500*8,C,i,tor[1],z)
    #         print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    # #ABPNACK
    # print("ABPNACK Simulation Results")
    # for i in timeOutList5ms:
    #     for z in BER:
    #         totalsend = ABPsenderNACK(H,1500*8,C,i,tor[0],z)
    #         print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    # for i in timeOutList5ms:
    #     for z in BER:
    #         totalsend = ABPsenderNACK(H,1500*8,C,i,tor[1],z)
    #         print('timeoutTime:'+str(i)+'  BER:'+str(z)+'  totalpacket:'+str(totalpacket) + '  totalTime:' + str(current_time)+'Throughput:' + str(totalpacket*1500*8/current_time))
    # #GBN
    print("GBN Simulation Results")
    t1 = ABPsender(H,1500*8,C,0.0125,tor[0],0)
    #totalsend = GBNsender(H,1500*8,C,0.0125,tor[0],0)
    #print('Throughput:' + str(1000*1500*8/current_time))
    print(t1)
if __name__ == '__main__':
    main()
