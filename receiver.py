import util
import os
import mysqlconnector as mycon


def pidregister(thispid, conninfo):
    query="UPDATE schedulerDB.realtime_status SET pid_receiver={};".format(thispid)
    mycon.db_write(conninfo, query)


def receiver(replyqueue, writeconnectioninfo, tracklck,
             runningjobdict):

    thispid = os.getpid()
    pidregister(thispid,writeconnectioninfo)
    try:
        while True:
            recv = replyqueue.get()
            tracklck.acquire()
            try:
                runningjobdict[str(recv[0])] = 0
            finally:
                tracklck.release()
            if recv[1] != 0:
                util.sendlog(writeconnectioninfo, recv[2], recv[3])
            util.logsubmit(writeconnectioninfo, recv[0], recv[1], recv[3])
    finally:
        query = "UPDATE schedulerDB.realtime_status SET pid_receiver={};".format(0)
        mycon.db_write(writeconnectioninfo, query)