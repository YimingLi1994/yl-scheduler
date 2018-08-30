import json
import multiprocessing as mp
import socketserver
import subprocess as sp
import time

import myjob as mj
import mysqlconnector as mycon
import worker
from settings import KNOWN_HOST, SOCKET_SERVER_PORT

'''Sample 
    {
        "operation":"sigint",
        "body":{
            "pid":"12345",
            "log_id":"123123",
            "jobchainid":"1234"
            }
    },
    {
        "operation":"insert",
        "body":{
            "jobchainid":"1234"
            }        
    }    
'''


def kill_check(log_id, writeconnectioninfo):
    querystr = '''select status from {}.jobchain_lst_run 
                where id = {}'''.format(writeconnectioninfo[4], log_id)
    res = mycon.db_read(writeconnectioninfo, querystr)
    status = res[0][0]
    if 'running' not in status:
        return True
    return False


def terminate_process(pid, jobchainid, log_id, writeconnectioninfo):
    querystr = '''select pid, status from {}.jobchain_lst_run 
                where jobchain_id={} and id = {}'''.format(writeconnectioninfo[4], jobchainid, log_id)
    res = mycon.db_read(writeconnectioninfo, querystr)
    if len(res) != 1:
        raise RuntimeError('No result returned')
    log_pid = res[0][0]
    status = res[0][1]
    if status != 'RUNNING...':
        raise RuntimeError('The job is not running')
    if log_pid != pid:
        raise RuntimeError('Mismatched pid')
    else:
        shellstr = '''sudo kill -sigint {}'''.format(pid)
        try:
            a = sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE, timeout=5)
            time.sleep(1)
            if a.returncode == 0:
                counter = 5
                while kill_check(log_id, writeconnectioninfo) is False:
                    counter -= 1
                    time.sleep(1)
                    if counter == 0:
                        raise RuntimeError('Cannot kill this job')
            else:
                raise RuntimeError(a.stderr.decode('ascii', 'ignore'))
        except sp.TimeoutExpired:
            raise RuntimeError('Time out, Please try again')


def insert_job(jobchainid, replyqueue, readconnectioninfo, writeconnectioninfo, envinfo,
               tracklck, runningjobdict):
    bkpflag = envinfo[0]
    flagstr = 'main_flag'
    typestr = 'main'
    if bkpflag == 1:
        typestr = 'bkp'
        flagstr = 'BKP_flag'

    query = \
        "SELECT id,timestr, dep_ot ,job_desc " \
        "FROM {}.jobchain_table " \
        "WHERE id={} and {}=1; ".format(readconnectioninfo[4], jobchainid, flagstr)
    res = mycon.db_read(writeconnectioninfo, query)
    if len(res) != 1:
        raise RuntimeError('{} does not have jobchain {}'.format(typestr, jobchainid))
    row = res[0]
    eachjc = mj.Myjobchain(row[0], row[1], None, row[2], row[3])
    tracklck.acquire()
    errorlst = []
    try:
        if str(jobchainid) in runningjobdict and runningjobdict[str(jobchainid)] == 1:
            errorlst.append((0, eachjc))
        else:
            runningjobdict[str(eachjc.id)] = 1
            p = mp.Process(target=worker.worker,
                           args=(eachjc, replyqueue,
                                 readconnectioninfo,
                                 writeconnectioninfo,
                                 envinfo))
            p.start()
    finally:
        tracklck.release()
    for eacherrjc in errorlst:
        if eacherrjc[0] == 0:
            raise RuntimeError('Job Id: {} not finished'.format(eacherrjc[1].id))


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.settimeout(2)
        peer_ip = self.request.getpeername()[0]
        if peer_ip not in KNOWN_HOST:
            return
        self.data = self.request.recv(1024).strip().decode('ascii', 'ignore')
        # print(self.data)
        print(self.data)
        retstr = 'bad request'
        try:
            opt = json.loads(self.data)
            if opt['operation'] == 'sigint':
                terminate_process(opt['body']['pid'],
                                  opt['body']['jobchainid'],
                                  opt['body']['log_id'],
                                  self.server.writeconnectioninfo)
                retstr = 'successfull'
            elif opt['operation'] == 'insert':
                insert_job(opt['body']['jobchainid'],
                           self.server.replyqueue,
                           self.server.readconnectioninfo,
                           self.server.writeconnectioninfo,
                           self.server.envinfo,
                           self.server.tracklck,
                           self.server.runningjobdict,
                           )
                retstr = 'successfull'
            else:
                raise RuntimeError('''Unknown operation''')
        except json.decoder.JSONDecodeError:
            retstr = 'bad request'
        except RuntimeError as e:
            retstr = str(e)
        except KeyError:
            retstr = 'bad request'
        finally:
            retstr_b = retstr.encode('ascii')
            self.request.sendall(retstr_b)


def status_server(replyqueue, readconnectioninfo, writeconnectioninfo, envinfo,
                  tracklck, runningjobdict):
    server = socketserver.TCPServer(('', SOCKET_SERVER_PORT), MyTCPHandler)
    server.replyqueue = replyqueue
    server.readconnectioninfo = readconnectioninfo
    server.writeconnectioninfo = writeconnectioninfo
    server.envinfo = envinfo
    server.tracklck = tracklck
    server.runningjobdict = runningjobdict
    server.serve_forever()
