import ipgetter
from settings import SOCKET_SERVER_PORT
from settings import NODE_TYPE
from settings import DATABASES
import mysqlconnector as mycon

def register(EXTERNAL_IP):
    dbconnectioninfo = [DATABASES['scheduler_control']['HOST'],
                           int(DATABASES['scheduler_control']['PORT']),
                    DATABASES['scheduler_control']['USER'],
                    DATABASES['scheduler_control']['PASSWORD'],
                    DATABASES['scheduler_control']['NAME']]

    #EXTERNAL_IP = ipgetter.myip()

    querystr='''select count(*) from {}.registered_scheduler 
                where machine_ip = \'{}\''''.format(dbconnectioninfo[4],EXTERNAL_IP)
    res = mycon.db_read(dbconnectioninfo, querystr)[0][0]

    if res == 1: ## Exists
        querystr='''UPDATE {}.registered_scheduler SET 
                    machine_port={}, machine_role='{}'
                    where machine_ip = '{}'  '''\
            .format(dbconnectioninfo[4],SOCKET_SERVER_PORT, NODE_TYPE, EXTERNAL_IP)
        mycon.db_write(dbconnectioninfo, querystr)

    else: ## Not Exists
        querystr='''INSERT INTO {}.registered_scheduler
                    (machine_ip, machine_port, machine_role) VALUES ('{}',{},'{}')'''\
                    .format(dbconnectioninfo[4],EXTERNAL_IP, SOCKET_SERVER_PORT, NODE_TYPE)
        mycon.db_write(dbconnectioninfo, querystr)



