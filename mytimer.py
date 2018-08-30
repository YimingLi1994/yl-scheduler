import datetime as dt
import pytz
import multiprocessing as mp
import time
import os
import mysqlconnector as mycon


def pidregister(thispid, conninfo):
    query = "UPDATE schedulerDB.realtime_status SET pid_timer={};".format(thispid)
    mycon.db_write(conninfo, query)


def timer(timestampqueue: mp.Queue, writeconnectioninfo):
    lsttime = None
    granularity = 60
    thispid = os.getpid()

    pidregister(thispid, writeconnectioninfo)
    # ###
    # debugtimenow = dt.datetime \
    #     .now(pytz.timezone('America/Chicago')) \
    #     .replace(tzinfo=None, second=0, microsecond=0)
    # timestampqueue.put(debugtimenow)
    # ###
    try:
        while True:
            timenow = dt.datetime \
                .now(pytz.timezone('America/Chicago')) \
                .replace(tzinfo=None, microsecond=0)
            if lsttime is None:
                lsttime = timenow.replace(second=0)
            if (timenow - lsttime).seconds / granularity >= 1:
                lsttime = timenow.replace(second=0)
                timestampqueue.put(timenow)
            time.sleep(0.1)
    finally:
        query = "UPDATE schedulerDB.realtime_status SET pid_timer={};".format(0)
        mycon.db_write(writeconnectioninfo, query)
