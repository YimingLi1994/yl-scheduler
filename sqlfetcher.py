import datetime as dt
import multiprocessing as mp
import os

import numpy as np
import pandas as pd
from croniter import croniter

import myjob as mj
import mysqlconnector as mycon
import util
import worker


def pidregister(thispid, conninfo):
    query = "UPDATE schedulerDB.realtime_status SET pid_sqlfetcher={};".format(thispid)
    mycon.db_write(conninfo, query)


def jobchain_timestrcheck(jobchain: mj.Myjobchain):
    return croniter.is_valid(jobchain.timestr)

def get_next_run_time(timestr, thistimestamp):
    cronbase = croniter(timestr, thistimestamp)
    base = cronbase.get_prev(dt.datetime)
    nextruntime = cronbase.get_next(dt.datetime)
    return nextruntime

def jobcheck(job_Chain: mj.Myjobchain, thistimestamp):
    if get_next_run_time(job_Chain.timestr, thistimestamp) == thistimestamp:
        return True
    return False

def sqlfetcher(timestampqueue: mp.Queue, replyqueue, readconnectioninfo, writeconnectioninfo, envinfo,
               tracklck, runningjobdict
               ):
    thispid = os.getpid()
    pidregister(thispid, writeconnectioninfo)
    bkpflag = envinfo[0]
    runningprocessdict = {}
    typestr = 'main'
    flagstr = 'main_flag'
    if bkpflag == 1:
        typestr = 'bkp'
        flagstr = 'BKP_flag'

    try:
        while True:
            exetime = timestampqueue.get()  # get timestamp
            query = \
                "SELECT id, timestr, dep_ot ,job_desc " \
                "FROM schedulerDB.jobchain_table " \
                "WHERE switch='ON' and {}=1; ".format(flagstr)
            read_cur = mycon.db_read(readconnectioninfo, query)

            query = \
                "SELECT jobchain_id, MAX(last_run_start) FROM schedulerDB.jobchain_lst_run " \
                "GROUP BY jobchain_id ORDER BY jobchain_id;"

            write_cur = mycon.db_read(writeconnectioninfo, query)
            if len(write_cur) == 0:
                tempnp = np.array([[-1, -1]])
            else:
                tempnp = np.array(write_cur)
            pdframe = pd.DataFrame(tempnp, index=tempnp[:, 0])

            jobChainlst = []
            for row in read_cur:
                lstrun = None
                if row[0] in pdframe.index:
                    lstrun = pdframe.loc[[row[0]]].values[0, 1]
                jobChainlst.append(mj.Myjobchain(row[0], row[1], lstrun, row[2], row[3]))
            errorlst = []

            for eachjc in jobChainlst:
                if jobchain_timestrcheck(eachjc) is False:
                    errorlst.append((1, eachjc))
                    ## Turn off that jobchain
                    querystr = '''update jobchain_table set switch = 'OFF' where id = {};'''.format(eachjc.id)
                    mycon.db_write(writeconnectioninfo, querystr)
                    continue
                if jobcheck(eachjc, exetime) is False:
                    continue
                tracklck.acquire()
                try:
                    if str(eachjc.id) in runningjobdict and runningjobdict[str(eachjc.id)] == 1:
                        errorlst.append((0, eachjc))
                    else:
                        runningjobdict[str(eachjc.id)] = 1
                        # worker.worker(eachjc, replyqueue,
                        #                      readconnectioninfo,
                        #                      writeconnectioninfo,
                        #                      envinfo)
                        p = mp.Process(target=worker.worker,
                                       args=(eachjc, replyqueue,
                                             readconnectioninfo,
                                             writeconnectioninfo,
                                             envinfo))
                        runningprocessdict[str(eachjc.id)] = p
                        runningprocessdict[str(eachjc.id)].start()
                finally:
                    tracklck.release()
            for eacherrjc in errorlst:
                if eacherrjc[0] == 0:
                    util.sendlog(writeconnectioninfo, 'Job Id: {} not finished'.format(eacherrjc[1].id))
                elif eacherrjc[0] == 1:
                    util.sendlog(writeconnectioninfo, 'Job Id: {} invalid timestr'.format(eacherrjc[1].id))
    finally:
        query = "UPDATE schedulerDB.realtime_status SET pid_sqlfetcher={};".format(0)
        mycon.db_write(writeconnectioninfo, query)
