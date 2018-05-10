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
    print("go")
    # RECHERCHER LE SCREENNAME DU COMPTE
    maxId = mdb.tweets.find().sort("id",-1).limit(1)
    maxId = maxId[0]['id'] if maxId else 0
    print('likes',len(todo['like']))
    for id in todo['like'].keys():
        #if id<=maxId:
        #    continue
        if 1:#try:
            sleep(random.random()/2)
            api.CreateFavorite(status_id=id, include_entities=False)
            mdbrw.logs.insert_one({'username':userdata['username'],'action':'like','tweet_id':id})
        #except Exception as err:
        #    pass
        #    print(err.message)

    print('rt',len(todo['rt']))
    for id in todo['rt'].keys():
        #if id<=maxId:
        #    continue
        if 1:#try:
            sleep(random.random()/2)
            api.PostRetweet(status_id=id,trim_user=True)
            mdbrw.logs.insert_one({'username':userdata['username'],'action':'rt','tweet_id':id})
        #except Exception as err:
        #    pass
        #    print(err.message)
    print("done")

def worker(n):
	while True:
		item = q.get()
		print('worker %d' % n,item)
		dotask(**item)
		q.task_done()



for i in range(nbworkers):
    workthread = Thread(target=worker,args=(i,))
    workthread.daemon = True
    workthread.start()
