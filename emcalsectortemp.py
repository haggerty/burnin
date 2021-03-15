#!/bin/env python

import sys
import telnetlib
import sqlite3
import datetime
import time

# Read temperatures

# John Haggerty, BNL, 2017.01.19

HOST = sys.argv[1]
PORT = "9760"

try:
    tn = telnetlib.Telnet(HOST,PORT)
except Exception as ex:
    print(ex)
    print("cannot connect to controller... give up")
    sys.exit()

tn.write(b"\n\r")
tn.write(b"\n\r")

nib = 6

for ib in range(0, nib):

    command = '$T'
    command += str(ib)
    print(command)
    tn.write(command.encode('ascii')+b"\n\r")
#    tn.write("$T1")
    x = tn.read_until(b">")
    line = x.decode('ascii')
#    print(line)
    tn.write(b"\n\r")

    sline = line.rstrip()
    line = sline.lstrip()
    line = line.replace('\r', '')
    tstr = str(line)
    readback = tstr.split('\n')
    
    readback.remove('>')
#    print(readback)

    temps = [float(i) for i in readback]
    twodecimals = ["%.2f" % v for v in temps]
#    print(temps)

    row_of_temp = '|  '
    for j, t in enumerate(twodecimals):
#            print("T {}: {}".format(j, t))
            row_of_temp += str(t)
            row_of_temp += ' '
            if j%2 == 1:
                row_of_temp += '  |  '
            if j%8 == 7:
                print(row_of_temp)
                row_of_temp = '|  '
            if j>32:
                break

    
