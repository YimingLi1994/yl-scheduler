import MySQLdb
import datetime as dt
import pytz
import mysqlconnector as mycon


def sendlog(writeconninfo, msg, showid=None):
    msgstr = str(msg)[-4000:]
    msgstr.strip()
    msgstr = msgstr.replace('\'', '\"')
    msgstr = MySQLdb.escape_string(msgstr)
    querystr = "INSERT INTO schedulerDB.schedulerMessage (msg) VALUES (\'{}\')".format(
        msgstr.decode('ascii', 'ignore'))
    if showid != None:
        querystr = "INSERT INTO schedulerDB.schedulerMessage " \
                   "(run_id, msg) VALUES ({},\'{}\')".format(showid, msgstr.decode('ascii', 'ignore'))
    mycon.db_write(writeconninfo, querystr)


def logsubmit(writeconninfo, jc_id, cond, showid):
    if cond == 0:
        cond = 0
        log = 'Success'
    else:
        cond = 1
        log = 'Failed'
    timenowstr = dt.datetime.now(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d %H:%M:%S")
    # querystr = "INSERT INTO schedulerDB.logtable (log,jobchain_id,run_result,entry_time) \
    #             VALUES (\"{}\",{},{},\'{}\');".format(log, jc_id, cond, timenowstr)
    # cur.execute(querystr)
    querystr = "UPDATE schedulerDB.jobchain_lst_run SET last_run_end=\'{}\', status=\'{}\' \
                WHERE id={};".format(timenowstr, log, showid)
    mycon.db_write(writeconninfo, querystr)
