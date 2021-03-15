#!/bin/env python3

# John Haggerty, BNL
# 2021.03.10

import justpy as jp
import pandas as pd
import time
import asyncio
from lvcontrol import *

controller_ip = '10.20.34.120'
nslots = 8

def button_click(self,msg):
    print(self.slot,self.onoff)
    tn = lv_connect(controller_ip)
    lv_enable(tn,self.slot,self.onoff)
    lv_disconnect(tn)

chnames = ['Slot', 'IB0P','IB1P','IB2P','IB3p','IB4P','IB5P','IB6P','IB7P',
                 'IB0N','IB1N','IB2N','IB3N','IB4N','IB5N','IB6N','IB7N']

wp = jp.WebPage(delete_flag=False)
wp.title = 'EMCAL LV'

header_div = jp.Div(text='EMCAL LV Burnin', a=wp, classes = 'text-5xl text-white bg-blue-500 hover:bg-blue-700 m-1')
time_div = jp.Div(a=wp, classes = 'text-1xl text-white bg-blue-500 hover:bg-blue-700 m-1')
the_time = jp.P(a=time_div)
on_button_div = jp.Div(a=wp)
off_button_div = jp.Div(a=wp)
button_classes = 'w-32 mr-2 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full'

for i in range(nslots):
        b = jp.Button(text=f'ON {i+1}', a=on_button_div, classes=button_classes, click=button_click)
        b.slot = i+1
        b.onoff = 1

for i in range(nslots):
        b = jp.Button(text=f'OFF {i+1}', a=off_button_div, classes=button_classes, click=button_click)
        b.slot = i+1
        b.onoff = 0

data_div = jp.Div(a=wp)
gridv = jp.AgGrid(a=data_div)
gridv.options.pagination = True
gridv.options.paginationAutoPageSize = True

async def voltages():
    while True:
        the_time.text = time.strftime("%a, %d %b %Y, %H:%M:%S", time.localtime())
        all_readings = []
        tn = lv_connect(controller_ip)
        for i in range(nslots):
            voltages = lv_readv(tn,i+1)
#            print('Voltages Slot: ',i+1,voltages)
            voltages.insert(0,'V'+str(i+1))
            all_readings.append(voltages)

            currents = lv_readi(tn,i+1)
#            print('Currents Slot: ',i+1,currents)
            currents.insert(0,'I'+str(i+1))
            all_readings.append(currents)

        lv_disconnect(tn)

        dfreadings = pd.DataFrame(all_readings,columns=chnames)
        gridv.load_pandas_frame(dfreadings)
        jp.run_task(wp.update())
        await asyncio.sleep(1)

async def voltages_init():
    jp.run_task(voltages())

async def voltages_test():
    return wp

jp.justpy(voltages_test, startup=voltages_init)
