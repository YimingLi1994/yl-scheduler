import platform
SchedulerDB = {
    'NAME': 'schedulerDB',
    'USER': 'yiming',
    'PASSWORD': 'yiming123',
    'HOST': '130.211.206.49',
    'PORT': 3306,
}
SchedulerDBBKP = {
    'NAME': 'schedulerDB',
    'USER': 'yiming',
    'PASSWORD': 'yiming123',
    'HOST': '146.148.79.143',
    'PORT': 3306,
}


AllowHost = ['127.0.0.1',
             '35.224.121.101', #upload-1 ExternalIP
             '104.197.118.95',   #upload-1 InternalIP
             ]

if platform.node() == 'yiming2':
    ROLE ='BKP' # ''/BKP
elif platform.node() == 'yiming1':
    ROLE = ''
else:
    raise ValueError('Please run jobkiller on yl-scheduler node')

IP = ''
PORT = 7412
