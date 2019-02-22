"""
This controller class controlls all the components of the scheduler 
"""

import multiprocessing as mp
import mytimer
import sqlfetcher
import platform
import worker
import receiver
import time
import os
import sys
import mysqlconnector as myconn


class Myscheduler:
    def __init__(self):
        nodeinfo = platform.node()
        self.envinfo = ()  # envinfo(bkpflag, pathbase jobfolder, depfolder, pythonpath)
        # self.readconnectioninfo = ["104.198.219.159", 3306, "yli003", "yli003", "schedulerDB"]  # for reading data
        # self.writeconnectioninfo = ["104.198.219.159", 3306, "yli003", "yli003", "schedulerDB"]  # for writing data

        if nodeinfo == 'yiming1': #< ------- main scheduler name
            self.envinfo += (0,)
            pathbase = '/home/yiming/jobs'  #< -------- chmod 777 if permission error staging running code.
            pythonpath = '/usr/bin/python3'   #< ------- default python path
            self.readconnectioninfo = ["130.211.206.49", 3306, "yiming", "yiming123", "schedulerDB"]  # for reading data
            self.writeconnectioninfo = ["130.211.206.49", 3306, "yiming", "yiming123", "schedulerDB"]  # for writing data
        elif nodeinfo == 'yiming2': #< ------- bkp scheduler name
            self.envinfo += (1,)
            pathbase = '/home/yiming/jobs'
            pythonpath = '/usr/bin/python3'
            self.readconnectioninfo = ["130.211.206.49", 3306, "yiming", "yiming123", "schedulerDB"]  # for reading data
            self.writeconnectioninfo = ["146.148.79.143", 3306, "yiming", "yiming123", "schedulerDB"]  # for writing data
        else:
            raise NameError('Unknown host')
        self.envinfo += (pathbase,)
        self.envinfo += ('{}/jobfolder/'.format(pathbase),)
        self.envinfo += ('{}/depfolder/'.format(pathbase),)
        self.envinfo += (pythonpath,)
        if self.scheduler_status_check() is False:
            pass
            #raise NameError('Scheuler is already running')
        try:
            self.mgr = mp.Manager()
        except:
            print(str(sys.exc_info()))
        finally:
            pass
        self.runningjobdict = self.mgr.dict()
        self.runningprocessdict = self.mgr.dict()
        self.tracklck = mp.Lock()

        self.timestampqueue = mp.Queue()
        self.replyqueue = mp.Queue()

        self.timer = mp.Process(target=mytimer.timer,
                                args=(self.timestampqueue,
                                      self.writeconnectioninfo))
        self.fetcher = mp.Process(target=sqlfetcher.sqlfetcher,
                                  args=(self.timestampqueue,
                                        self.replyqueue,
                                        self.readconnectioninfo,
                                        self.writeconnectioninfo,
                                        self.envinfo,
                                        self.tracklck,
                                        self.runningjobdict,
                                        ))
        self.receiver = mp.Process(target=receiver.receiver,
                                   args=(self.replyqueue,
                                         self.writeconnectioninfo,
                                         self.tracklck,
                                         self.runningjobdict,
                                         ))

        self.timer.start()
        self.fetcher.start()
        self.receiver.start()

    def idle(self):
        bkpflag = self.envinfo[0]
        typestr = 'main'
        if bkpflag == 1:
            typestr = 'bkp'
        try:
            while True:
                query = "UPDATE schedulerDB.realtime_status SET timequeuesize={}, replyqueuesize={}, " \
                        "index_last_ping_time=NOW() " \
                        "WHERE name = '{}';".format(self.timestampqueue.qsize(),
                                                    self.replyqueue.qsize(),
                                                    typestr)
                myconn.db_write(self.writeconnectioninfo, query)
                time.sleep(20)
        finally:
            query = "UPDATE schedulerDB.realtime_status SET pid_index={} WHERE name = '{}';".format(0, typestr)
            myconn.db_write(self.writeconnectioninfo, query)

    def scheduler_status_check(self):
        bkpflag = self.envinfo[0]
        thispid = os.getpid()

        retflag = False
        typestr = 'main'
        if bkpflag == 1:
            typestr = 'bkp'
        query = "SELECT pid_index FROM schedulerDB.realtime_status " \
                "WHERE name = '{}';".format(typestr)
        retans = myconn.db_read(self.writeconnectioninfo, query)
        if len(retans) == 0:
            self.scheduler_status_init(thispid)
            retflag = True
        else:
            dbpid = retans[0][0]
            if dbpid == 0:
                query = "UPDATE schedulerDB.realtime_status SET pid_index={} WHERE name = '{}';".format(thispid,
                                                                                                        typestr)
                myconn.db_write(self.writeconnectioninfo, query)
                retflag = True
        return retflag

    def scheduler_status_init(self, thispid):
        bkpflag = self.envinfo[0]
        typestr = 'main'
        if bkpflag == 1:
            typestr = 'bkp'
        query = "INSERT INTO schedulerDB.realtime_status (name,pid_index,debugmode) " \
                "VALUES (\'{}\',{},\'{}\');".format(typestr, thispid, 'debug')
        myconn.db_write(self.writeconnectioninfo, query)
