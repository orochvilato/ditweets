# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread
from time import sleep
q = Queue()
import random
nbworkers = 8



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
