import MySQLdb
import time
from contextlib import closing


def db_connect(conninfo, timeout):
    conn = MySQLdb.connect(host=conninfo[0],
                           port=conninfo[1],
                           user=conninfo[2],
                           passwd=conninfo[3],
                           db=conninfo[4],
                           connect_timeout=timeout)
    return conn


def db_read(connectioninfo, querystr, timeout=5, retry=3600):
    retry_count = 0
    successflag = False
    retrowlst = None
    while retry_count < retry:
        try:
            retrowlst = []
            conn = db_connect(connectioninfo, timeout)
        except MySQLdb.Error as e:
            print('cannot connect mysql retry: {}'.format(retry_count))
            time.sleep(1)
            retry_count += 1
            continue
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(querystr)
                for row in cursor.fetchall():
                    retrowlst.append(row)
            successflag = True
        except MySQLdb.Error as e:
            print(e)
            retry_count += 1
            time.sleep(1)
        finally:
            conn.close()
            if successflag is True:
                break
    if successflag is True:
        return retrowlst
    else:
        raise RuntimeError('Cannot connect database')


def db_write(connectioninfo, querystr, timeout=5, retry=3600):
    retry_count = 0
    successflag = False
    ret_res = None
    while retry_count < retry:
        try:
            conn = db_connect(connectioninfo, timeout)
        except MySQLdb.Error as e:
            print('cannot connect mysql retry: {}'.format(retry_count))
            retry_count += 1
            time.sleep(1)
            continue
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(querystr)
                ret_res = cursor.lastrowid
            conn.commit()
            successflag = True
        except MySQLdb.Error as e:
            conn.rollback()
            print(e)
            retry_count += 1
            time.sleep(1)
        finally:
            conn.close()
            if successflag is True:
                break
    if successflag is True:
        return ret_res
    else:
        raise RuntimeError('Cannot connect database')
