import multiprocessing as mp
import time
import MySQLdb
import sys
import subprocess as sp
from timeit import default_timer as timer
import myjob
import fetchcode
import os
import datetime as dt
import pytz
import shutil
import traceback


def worker(job_chain: myjob.Myjobchain,
           replyqueue: mp.Queue,
           readconnectioninfo,
           writeconnectioninfo,
           envinfo):
    """
    each worker only can have one shadow process to do jobexec
    :param job_chain: myjob.Myjobchain
    :param replyqueue: {job_chain_id:status}:
    :param connectioninfo: (host,port,user,passwd,db):    
    
    :return:
    """
    thispid = os.getpid()
    bkpflag = envinfo[0]
    pathbase = envinfo[1]
    jobpath = envinfo[2]
    deppath = envinfo[3]
    pythonpath = envinfo[4]
    timenow = dt.datetime \
        .now(pytz.timezone('America/Chicago')) \
        .replace(tzinfo=None)
    job_chain.sendlstrun(writeconnectioninfo, timenow.strftime("%Y-%m-%d %H:%M:%S"), thispid)
    job_chain.fetchjob(readconnectioninfo)
    job_chain.fetchdep(readconnectioninfo)
    retstatus = 0
    msg = ""
    targetfolderclearlst = []
    try:
        start = timer()
        depPass = True
        while True:
            depPass = True
            for eachdep in job_chain.deplst:  # if needed this can be parallelized
                msg += 'dep: ' + str(eachdep.depid) + ', '
                targetbase = fetchcode.fetchcode(pathbase, 'dep', folderName=eachdep.rootfolder)
                targetfolderclearlst.append(targetbase)
                calllst = [eachdep.env]
                calllst.append(targetbase + '/' + eachdep.commandlst[0])
                if bkpflag == 1:
                    calllst.append('bkp')
                for idx in range(1, len(eachdep.commandlst)):
                    calllst.append(eachdep.commandlst[idx])
                try:
                    a = sp.run(calllst, stdout=sp.PIPE, stderr=sp.PIPE, timeout=eachdep.ottime, cwd=os.path.join(targetbase,eachdep.commandlst[0].split('/')[0]))
                    if a.returncode == 0:
                        if a.stdout.decode('ascii', 'ignore').strip() != '0':
                            depPass = False
                    else:
                        msg += a.stderr.decode('ascii', 'ignore')
                        depPass = False
                        #raise NameError("depjob Error, dep_id=" + eachdep.depid)
                except sp.TimeoutExpired:
                    depPass = False

            end = timer()
            if end - start > job_chain.ottime or depPass is True:
                break
            time.sleep(60)
        if depPass == True:
            ## UPDATE DEP_ts
            job_chain.send_dep_pass(writeconnectioninfo)
            for eachstep in sorted(list(set([eachjob.step for eachjob in job_chain.joblst]))):
                joblst = [eachjob for eachjob in job_chain.joblst if eachjob.step == eachstep]
                for eachjob in joblst:  # if needed this can be parallelized
                    msg += 'job: ' + str(eachjob.jobid) + ', '
                    targetbase = fetchcode.fetchcode(pathbase, 'job', folderName=eachjob.rootfolder)
                    targetfolderclearlst.append(targetbase)
                    calllst = [eachjob.env]
                    calllst.append(targetbase + '/' + eachjob.commandlst[0])
                    if bkpflag == 1:
                        calllst.append('bkp')
                    for idx in range(1, len(eachjob.commandlst)):
                        calllst.append(eachjob.commandlst[idx])
                    a = sp.run(calllst, stdout=sp.PIPE, stderr=sp.PIPE, timeout=eachjob.ottime, cwd=os.path.join(targetbase,eachjob.commandlst[0].split('/')[0]) )
                    if a.returncode != 0:  # filename
                        print('stderr: ' + a.stderr.decode('ascii', 'ignore'))
                        msg += a.stderr.decode('ascii', 'ignore')
                        raise NameError("Error Occor when executing job_id={}".format(eachjob.jobid))
                    retstatus += a.returncode
                    msg += a.stdout.decode('ascii', 'ignore')
        else:
            retstatus += 1
            msg = "dependent condition timeout"
    except sp.TimeoutExpired:
        retstatus = 1
        msg += 'executing time out'
    except Exception as e:
        retstatus = 1
        msg += str(traceback.format_exc())
    finally:
        for eachpath in targetfolderclearlst:
            shutil.rmtree(eachpath)
        replymessage = (job_chain.id, retstatus, str(msg), job_chain.showid)
        replyqueue.put(replymessage)
