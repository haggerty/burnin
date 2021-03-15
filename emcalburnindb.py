#!/bin/env python

import sys
import telnetlib
import sqlite3
import time
import os.path
import time
from datetime import datetime
from array import array
from pw import rw
from readbias import readbias

# John Haggerty, BNL, 2020.09.16

def et(HOST='10.20.34.10', state=1, events=0):

    PORT = "9760"

    try:
        tn = telnetlib.Telnet(HOST,PORT)
    except Exception as ex:
        print(ex)
        print("cannot connect to controller... give up")
        sys.exit()

#    dbfile = open('/data1/phnxrc/emcal/sectortest/burnin.sql','a+')
    dbfile = open('burnin.sql','a+')

# this the last run number
    runnumberfile = open(os.path.expandvars("$HOME/.rcdaqrunnumber.txt"),"r")
    runnumber = int( runnumberfile.readline() ) + state
    runnumberfile.close()

# timess in a couple of formats
    utime = array( 'd', [ 0.0 ] )
    utime[0] = time.time()
    now = datetime.now()
    readtime = now.strftime('%Y-%m-%d %H:%M:%S')

# get the sector number under test (don't forget to edit the file!)
    sectornumberfile = open(os.path.expandvars("$HOME/.emcsectornumber.txt"),"r")
    sectornumber = int( sectornumberfile.readline() )
    sectornumberfile.close()

## OLD: get the bias voltage from the Wiener... or at least the setpoint
#    bulkbiasfile =  open(os.path.expandvars("$HOME/BiasControl/sPHENIX_HVSet.txt"),"r")
#    firstline = bulkbiasfile.readline()
#    token = firstline.split()
#    bulkbias = float( token[1] )
## maybe I'll read it someday... just a placeholder for now
#    bulkcurrent = -1.0
#    bulkbiasfile.close()

# NEW: read the bias voltage and current from the Wiener
    (biasvolt,biascurrent) = readbias()

# dictionary to turn gain strings N or H to integer
    gaintoint = {'n':0, 'h':1}

# get the pulse width from the test pulse fanout
    tpwidth = rw()

#    sql = "INSERT INTO rundb(runnumber,sector,readtime,events) VALUES (%d,%d,\'%s\',%d);" % (runnumber,sectornumber,readtime,events)   
    sql = "INSERT INTO rundb(runnumber,sector,readtime,events) VALUES ({}, {}, \'{}\', {});"\
        .format(runnumber,sectornumber,readtime,events)
    print(runnumber,utime[0],readtime,sectornumber,biasvolt,biascurrent,tpwidth)
    print(sql)
    dbfile.write(sql+'\n')

    tn.write( b"\n\r" )
    tn.write( b"\n\r" )

    for ib in range(0, 6):

        command = '$V'
        command += str(ib)
        print(command)
        tn.write(command.encode())
        line = tn.read_until(b'>',2)
        print(line)

        tn.write( b"\n\r" )

        command = '$E'
        command += str(ib)
        print(command)
        tn.write(command.encode())
        line = tn.read_until(b"\r#00000\r!",2)
        line = line.decode()
        line = line.replace('\r', '')
#       line = line.replace('#', '')
        line = line.replace('!', '')
        print(line)

        tn.write( b"\n\r" )

        sentence = line.split('#')

#    print('items returned: ',len(sentence))
#    print(sentence)

        sql = "INSERT INTO iface (runnumber, sector, ib, readtime, tpwidth, biasvolt, biascurrent) VALUES ({}, {}, {},\'{}\', {}, {}, {});"\
            .format(runnumber,sectornumber,ib,readtime,tpwidth,biasvolt,biascurrent)
        print(sql)
        dbfile.write(sql+'\n')

        sentence_number = 0
        for s in sentence:
            ss = s.rstrip(",\r")
            word = ss.split(',')
            print('sentence_number: ',sentence_number,' entries: ',len(word)) 
            print(word)
            if sentence_number == 1:
                ipaddr = word[0]
                ibrb = int( word[1] )
                version = word[2]
                sql = "UPDATE burnin SET "\
                    "ipaddr=\'{}\', version=\'{}\' "\
                    "WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(ipaddr,version,runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 2:
                calmode = word[0]
                print(word[1])
#                gain = gaintoint[word[1].lower()]
# everything seems to return 0 or 1 now                
                gain = int(word[1])
                stabilizer = word[2]
                commled = word[3]
                loopres = float( word[4] )
                tempco = float( word[5] )
                biascalcon = float( word[6] )
                sql = "UPDATE burnin SET "\
                    "calmode=\'{}\', gain={}, stabilizer={}, commled={}, "\
                    "loopres={}, tempco={}, biascalcon={} "\
                    "WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(calmode,gain,stabilizer,commled,loopres,tempco,biascalcon,\
                    runnumber,sectornumber,ib,readtime)
                print(sql)    
                dbfile.write(sql+'\n')

            if sentence_number == 3:
                vp = word[0]
                vn = word[1]
                vb = word[2]
                sql = "UPDATE burnin SET "\
                    "vp={}, vn={}, vb={} "\
                    "WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(vp,vn,vb,runnumber,sectornumber,ib,readtime)
                print(sql)    
                dbfile.write(sql+'\n')

            if sentence_number == 4:
# decided to consolidate all interface board data into one table... may or may not be a good idea                
# keep this around in case of future breakup
# sql = "INSERT INTO ifacetower (runnumber, sector, ib) VALUES (%d, %d, %d);" % (runnumber, sectornumber, ib)
                towercurrent = ','.join(word)
                print(towercurrent)
                sql = "UPDATE burnin SET towercurrent = \'{"\
                    +towercurrent+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')
           
            if sentence_number == 5:
# little kluge to save only 32 thermistors (which is all there are)
                thermistorsipm = ','.join(word[0:32:2])
                print(thermistorsipm)
                sql = "UPDATE burnin SET thermistorsipm= \'{"\
                    +thermistorsipm+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')
                thermistorpa = ','.join(word[1:32:2])
                print(thermistorsipm)
                sql = "UPDATE burnin SET thermistorpa= \'{"\
                    +thermistorpa+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 6:
                dac = ','.join(word)
                print(dac)
                sql = "UPDATE burnin SET dac = \'{"\
                    +dac+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 7:
                trimmv = ','.join(word)
                print(trimmv)
                sql = "UPDATE burnin SET trimmv = \'{"\
                    +trimmv+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 8:
                compimv = ','.join(word)
                print(compimv)
                sql = "UPDATE burnin SET compimv = \'{"\
                    +compimv+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 9:
                comptmv = ','.join(word)
                print(comptmv)
                sql = "UPDATE burnin SET comptmv = \'{"\
                    +comptmv+\
                    "}}\' WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(runnumber,sectornumber,ib,readtime)
                print(sql)
                dbfile.write(sql+'\n')

            if sentence_number == 10:
                tpmask = word[0]
                sql = "UPDATE burnin SET "\
                    "tpmask={} "\
                    "WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(tpmask,runnumber,sectornumber,ib,readtime)
                print(sql)    
                dbfile.write(sql+'\n')

            if sentence_number == 11:
                ledmask = word[0]
                sql = "UPDATE burnin SET "\
                    "ledmask={} "\
                    "WHERE runnumber={} AND sector={} AND ib={} AND readtime='{}';"\
                    .format(ledmask,runnumber,sectornumber,ib,readtime)
                print(sql)    
                dbfile.write(sql+'\n')

            sentence_number += 1
    
    print("closing append to dbfile...")
    dbfile.close()

# main

def main():
    try:
        HOST = sys.argv[1]
    except IndexError:
        HOST = '10.20.34.10'
    et(HOST)

if __name__ == "__main__":
    main()
