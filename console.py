#!/bin/env python3

# John Haggerty, BNL
# 2021.02.17

from lvcontrol import *
import time

tn = lv_connect('10.20.34.120')
for i in range(8):
    voltages = lv_readv(tn,i+1)
    print('Voltages Slot ',i+1,voltages)
    currents = lv_readi(tn,i+1)
    print('Currents Slot ',i+1,currents)
lv_disconnect(tn)    
