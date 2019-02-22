import os
import subprocess
import sys
import uuid
import shutil
import platform


def fetchcode(pathbase, dest, folderName):
    """
    
    :param dest: dep/job 
    :param folderName: 
    :return: 
    """
    retry_num = 10
    if dest == 'dep':
        jobfolder = 'depfolder'
    elif dest == 'job':
        jobfolder = 'jobfolder'

    else:
        raise NameError('dest only can be \'dep\' or \'job\'')
    pathbase = os.path.join(pathbase,jobfolder ,str(uuid.uuid4()))
    targetfolder = os.path.join(pathbase, folderName)
    node = platform.node()
    if node in ('LAPTOP-MRA1E0VJ','yiming1','yiming2'):
        shellstr = 'gsutil -m rsync -d -r gs://yiming-scheduler/{0}/{1} {2}'.format(jobfolder, folderName, targetfolder)
    else:
        shellstr = 'gsutil -m rsync -d -r gs://dp-scheduler-test/{0}/{1} {2}'.format(jobfolder, folderName,
                                                                                     targetfolder)
    shelllst = shellstr
    try_count = 0
    while try_count < retry_num:
        try:

            a = subprocess.run('mkdir {}'.format(pathbase), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if a.returncode != 0:
                raise ValueError(a.stderr.decode('ascii', 'ignore'))
            a = subprocess.run('mkdir {}'.format(targetfolder), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
            if a.returncode != 0:
                raise ValueError(a.stderr.decode('ascii', 'ignore'))
            a = subprocess.run(shelllst, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, shell = True)
            if a.returncode != 0:
                raise ValueError(a.stderr.decode('ascii', 'ignore'))
            break
        except:
            try_count += 1
            shutil.rmtree(pathbase)
            continue
    if try_count == retry_num:
        raise RuntimeError('Cannot fetch code from storage, the shellstr is {}'.format(shelllst))
    return pathbase
