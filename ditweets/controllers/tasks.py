# -*- coding: utf-8 -*-
from ditweets.auth import auth
from queue import Queue
from threading import Thread
from time import sleep
q = Queue()
import random
nbworkers = 8


import subprocess
import twitter



def dotask(userdata,todo):
    from ditweets.controllers.twitter import twitterAccount
    from ditweets import mdb, mdbrw

    api = twitterAccount(userdata)

    import json
    from datetime import datetime
    with open('/tmp/ditweets.log','a') as f:

        f.write('---- start %s (%s) ----\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),userdata.get('username','VIDE')))
        f.write("%s\n" % json.dumps(todo))
    # RECHERCHER LE SCREENNAME DU COMPTE
    #maxId = mdb.tweets.find().sort("id",-1).limit(1)
    #maxId = maxId[0]['id'] if maxId else 0
        for id in todo['like'].keys():
            log = {'username':userdata['username'],'action':'like','tweet_id':id}
            #if id<=maxId:
            #    continue
            try:
                sleep(random.random()/2)
                api.CreateFavorite(status_id=id, include_entities=False)
                mdbrw.logs.insert_one(log)
            except Exception as err:
                log['error'] = err.message
                f.write("Like %d : %s \n" % (id,err.message))



        for id in todo['rt'].keys():
            log = {'username':userdata['username'],'action':'rt','tweet_id':id}
            #if id<=maxId:
            #    continue
            try:
                sleep(random.random()/2)
                api.PostRetweet(status_id=id,trim_user=True)
                mdbrw.logs.insert_one(log)
            except Exception as err:
                log['error'] = err.message
                f.write("RT %d : %s \n" % (id,err.message))

        f.write('---- end %s (%s) ----\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), userdata.get('username','VIDE')))

def worker(n):

    while True:
        item = q.get()
        open('/tmp/ditweets.log','a').write('worker %d - %s\n' % (n,item['userdata']['username']))
        dotask(item)

        q.task_done()



for i in range(nbworkers):
    workthread = Thread(target=worker,args=(i,))
    workthread.daemon = True
    workthread.start()
