# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread
from time import sleep
q = Queue()
import random
nbworkers = 8


import subprocess

def ffmpeg(*cmd):
	try:
		subprocess.check_output(['ffmpeg'] + list(cmd))
	except subprocess.CalledProcessError:
		return False

	return True

def make_thumb(video_filename):
	# pad with black if W<H, crop to center if W>H, rescale to 300x300 if greater


	ff_filters = (f.replace(',', '\\,') for f in (
		'pad=if(lt(iw,ih),ih,iw):ih:if(lt(iw,ih),(ih-iw)/2,0):0:black',
		'crop=ih:ih:(iw-ih)/2:0',
		'scale=if(lt(iw,300),iw,300):if(lt(iw,300),iw,300)',
	))
	ff_filterstr = ','.join(ff_filters)

	thumb_path = video_filename + '.thumb.jpg'
	ffmpeg('-y', '-vf', ff_filterstr,
		'-vframes', '1', thumb_path,
		'-i', video_filename)

def worker(n):
    while True:
        item = q.get()
        retries = 3
        while retries>0:
            try:
                sleep(0.1+random.random())
                print('worker %d' % n,item)
                retries = -1
            except:
                retries -= 1

        if retries>=0:
            pass
            #states[item['key']] = {'etat':u'Erreur','avancement':-1}
        print('done',retries)
        q.task_done()



for i in range(nbworkers):
    workthread = Thread(target=worker,args=(i,))
    workthread.daemon = True
    workthread.start()
