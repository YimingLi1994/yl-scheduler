import platform
SchedulerDB = {
    'NAME': 'schedulerDB',
    'USER': 'yiming',
    'PASSWORD': 'yiming',
    'HOST': '35.224.121.101',
    'PORT': 3306,
}
SchedulerDBBKP = {
    'NAME': 'schedulerDB',
    'USER': 'yiming',
    'PASSWORD': 'yiming',
    'HOST': '104.197.118.95',
    'PORT': 3306,
}


AllowHost = ['127.0.0.1',
             '35.224.121.101', #upload-1 ExternalIP
             '104.197.118.95',   #upload-1 InternalIP
             ]

if platform.node() == 'yl-louise':
    ROLE ='BKP' # ''/BKP
elif platform.node() == 'yl-shana':
    ROLE = ''
else:
    raise ValueError('Please run jobkiller on yl-scheduler node')

IP = ''
PORT = 7412
