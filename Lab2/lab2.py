from __future__ import print_function
import os
import sys
import argparse
import math
import random
import csv
import gc


BER = 0.01

class Event:
    def __init(self,itype,time,error_flag,sequence_number):
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
    return alistz       

def ABPsender(H,l,C):
    # initialization
    ES = []
    SN = 0
    next_expected_ack =(SN+1)%2
    TimeOutTime=100
    current_time = 0
    packetLength = H+l
    # H is header length, l is packet length


    TimeOutEvent = current_time+packetLength/C+TimeOutTime
    ES = addTimeOutEvent(ES,TimeOutEvent,SN)
    result = send(SN,packetLength,current_time)
    if(result.type != 'NIL'):
        ES.append(result)
        ES = mergeSort(ES)
    while(ES):
        i = ES[0]
        ES.remove(i)
        #TODO update current time
        if(i.type == 'TimeOutEvent'):
            TimeOutEvent = current_time+packetLength/C+TimeOutTime
            ES = addTimeOutEvent(ES,TimeOutEvent,SN) 
            result = send(SN,packetLength,current_time)
            if(result.type != 'NIL'):
                ES.append(result)
                ES = mergeSort(ES)
        else if (i.type == 'ACKEvent'):
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


def clearTimeOutEvent(ES):
    for i in ES:
        if(i.type == 'TimeOutEvent'):
            ES.remove(i)
    
    return ES
            

def addTimeOutEvent(ES,time,SN):
    TimeOutEvent = Event('TimeOutEvent',time,0,SN)
    ES.append(TimeOutEvent)
    return mergeSort(ES)

def send(Time,SN,packetLength):
    ploss = 0.2
    propDelay = 0.1
    #BER (the probability that a bit arrives in error, considered independently from one bit to another
    #no error = (1-BER)^L
    #Perror = sigma(k=1->4)*LchooseK*BER^k*(1-BER)^(L-k)
    #PLoss = 1- Pnoerror - Perror
    forwardChannel(Time,SN,packetLength) # sender to recevier
    receiver()
    reverseChannel()# receiver to sender
    ACKEvent = Event('ACKEvent',time,error_flag,SN)
    return

def forwardChannel(Time,SN,packetLength):
    i = 0
    result = []
    while(i < len(packetLength)):
        i= i +1
        result.append(generate01())
    
    
    

def generate01():
    number = random.random()
    if(number <= BER):
        return 0
    else:
        return 1
        


def main():
    print("hey,60 boy")

if __name__ == '__main__':
    main()
