import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

### use the format so that this can be import directly into django settings.py
DATABASES = {
    'scheduler_shared': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scheduler_shared',
        'USER': 'root',
        'PASSWORD': '2212',
        'HOST': '127.0.0.1',
        'PORT': '4404',
    },
    'scheduler_main': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scheduler_main',
        'USER': 'root',
        'PASSWORD': '2212',
        'HOST': '127.0.0.1',
        'PORT': '4404',
    },
    'scheduler_bkp': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scheduler_bkp',
        'USER': 'root',
        'PASSWORD': '2212',
        'HOST': '127.0.0.1',
        'PORT': '4404',
    },
    'scheduler_control': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scheduler_platform',
        'USER': 'root',
        'PASSWORD': '2212',
        'HOST': '127.0.0.1',
        'PORT': '4404',
    },
}
GOOGLE_STORAGE = {
    'prod': {
        'dep': 'depfolder',
        'job': 'jobfolder',
        'project': 'shc-price-rec-prod',
        'bucket': 'dp-scheduler',
    },
    'debug': {  # For testing
        'dep': 'depfolder',
        'job': 'jobfolder',
        'project': 'shc-price-rec-prod',
        'bucket': 'dp-scheduler-test',
    },
}

TIME_ZONE = 'America/Chicago'

#### Set to false in production
RUNNING_MODE = 'debug' # prod/debug

#### Fill here either 'main' or 'bkp' (exclude quote)
NODE_TYPE = 'main' # main/bkp

MAX_CONCURRENCY=0  # TODO: rewrite to rpc mode

'''Continuous Number of dependency error occurred before fail the jobchain'''
DEP_ERR_TOLERENCE = 5 # TODO: Dependency error tolerence

'''job path base on the machine to cache the all jobs/deps locally before running'''
JOB_PATH_BASE = 'C:/Users/Jianw/OneDrive/work/jobbase'

'''python3 path on the machine'''
SCHEDULER_PYTHONPATH = 'C:\\Users\\Jianw\\AppData\\Local\\Programs\\Python\\Python36\\python.exe'

'''ONLY LISTEN TO THIS'''
KNOWN_HOST = ['127.0.0.1']

SOCKET_SERVER_PORT = 7513
