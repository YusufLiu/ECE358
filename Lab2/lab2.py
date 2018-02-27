from __future__ import print_function
import os
import sys
import argparse
import math
import random
import csv
import gc

class Time_out:
    def __init__(self,time):
        self.time = time

class ACK:
    def __init__(self,RN,status):
        self.RN = RN
        self.status = status

    def changeStatus(self,status):
        self.status = status
class Event:
    def __init(self,itype,time,error_flag,sequence_number):
        self.type= itype
        self.time = time
        self.error_flag = error_flag
        self.sequence_number = sequence_number


def ABPsender():
    SN = 0
    next_expected_ack =(SN+1)%2
    packet = getpacket()
    sent(SN,packet,t)


def send(Time,SN,packet):



def main():
    print("hey,60 boy")

if __name__ == '__main__':
    main()
