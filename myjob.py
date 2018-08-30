import re

import mysqlconnector as mycon
import datetime as dt
import pytz

class Myjobchain:
    def __init__(self, id: int,  timestr, lastrun, depot, desc):
        self.desc = desc
        self.workers = {}
        self.joblst = []
        self.deplst = []
        self.ottime = float(depot) * 60
        self.id = id
        #self.totalsteps = totalsteps
        self.lastrun = None
        # mytzinfo = dt.datetime.now(pytz.timezone('America/Chicago')).tzinfo
        if lastrun != None:
            self.lastrun = lastrun.replace(tzinfo=None, second=0, microsecond=0)
        self.timestr = ' '.join(['*' + str(x) if x[0] == '/' else x for x in \
                                    re.sub(' +', ' ', timestr).strip().split(' ')][:5])

        self.showid = None  # this is reserved for runtimelog

    def sendlstrun(self, conninfo, timestr, pid):  # dbwrite
        querystr = "INSERT INTO schedulerDB.jobchain_lst_run (jobchain_id, last_run_start, pid) " \
                   "VALUES ({},\'{}\', {});".format(
            self.id,
            timestr,
            pid
        )
        self.showid = mycon.db_write(conninfo, querystr)

    def send_dep_pass(self, conninfo):
        assert self.showid is not None, 'showid is None'
        timenowstr = dt.datetime.now(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d %H:%M:%S")
        querystr = "UPDATE schedulerDB.jobchain_lst_run SET dep_pass_ts=\'{}\' WHERE id={};".format(timenowstr,
                                                                                                    self.showid)
        mycon.db_write(conninfo, querystr)

    def fetchjob(self, conninfo):  # dbread
        querystr = \
            "SELECT id, step_lvl, env, command, ottime FROM schedulerDB.jobtable WHERE job_chain_id={};".format(self.id)
        rowtpl = mycon.db_read(conninfo, querystr)
        for row in rowtpl:
            self.joblst.append(Myjob(row[0], row[1], row[2], row[3], row[4]))
        self.joblst.sort(key=lambda temp: temp.step)

    def fetchdep(self, conninfo):  # dbread
        querystr = "SELECT id,env, command, ottime FROM schedulerDB.deptable WHERE jobchainid={};".format(self.id)
        rowtpl = mycon.db_read(conninfo, querystr)
        for row in rowtpl:
            self.deplst.append(Mydep(row[0], row[1], row[2], row[3]))


class Myjob:
    def __init__(self, jobid, step, env, command, ottime):
        self.jobid = jobid
        self.step = step
        self.env = env
        self.commandlst = command.split(';')
        for idx in range(0, len(self.commandlst)):
            self.commandlst[idx] = self.commandlst[idx].strip()
        self.rootfolder = self.commandlst[0].split('/')[0]
        self.ottime = int(float(ottime) * 60)


class Mydep:
    def __init__(self, depid, env, command, ottime):
        self.depid = depid
        self.env = env
        self.commandlst = command.split(';')
        for idx in range(0, len(self.commandlst)):
            self.commandlst[idx] = self.commandlst[idx].strip()
        self.rootfolder = self.commandlst[0].split('/')[0]
        self.ottime = int(float(ottime) * 60)
