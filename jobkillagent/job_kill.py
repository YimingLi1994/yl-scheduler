import subprocess as sp
import sqlalchemy
import time
import settings
import pandas as pd
def kill_job(id):
    schedulcerDict = settings.SchedulerDB
    if settings.ROLE == 'BKP':
        schedulcerDict = settings.SchedulerDBBKP
    querystr='''\
SELECT pid from jobchain_lst_run
where jobchain_id = {} and status = 'RUNNING...' and DATE(last_run_start)=CURDATE()
    '''.format(id)

    engine = sqlalchemy.create_engine('mysql://{}:{}@{}:{}/{}'.format(
        schedulcerDict['USER'],
        schedulcerDict['PASSWORD'],
        schedulcerDict['HOST'],
        schedulcerDict['PORT'],
        schedulcerDict['NAME'],
    ))
    df = pd.read_sql(querystr,engine)
    if df.shape[0] == 0:
        return {'id':id,
                'returncode':1,
                'msg':'Job already finished'
                }
    pidnum = df.values[0,0]
    print(pidnum)
    shellstr='sudo kill -sigint {}'.format(pidnum)
    sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
    ret=kill_check(id)
    if ret is False:
        return {'id':id,
                'returncode':5,
                'msg':'Killing timeout, Please retry'
                }
    else:
        return {'id': id,
                'returncode': 0,
                'msg': ''
                }

def kill_check(id,checktime=10, interval=0.5):
    schedulcerDict=settings.SchedulerDB
    if settings.ROLE == 'BKP':
        schedulcerDict = settings.SchedulerDBBKP

    querystr='''\
SELECT count(*) from jobchain_lst_run
where jobchain_id = {} and status = 'RUNNING...' and DATE(last_run_start)=CURDATE()
    '''.format(id)

    engine = sqlalchemy.create_engine('mysql://{}:{}@{}:{}/{}'.format(
        schedulcerDict['USER'],
        schedulcerDict['PASSWORD'],
        schedulcerDict['HOST'],
        schedulcerDict['PORT'],
        schedulcerDict['NAME'],
    ))
    checkpass=False
    for idx in range(checktime):
        res = pd.read_sql(querystr,engine).values[0,0]
        if res != 0:
            time.sleep(interval)
        else:
            checkpass=True
            break
    return checkpass



