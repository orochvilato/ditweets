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

def get_user_stats():
    pass

def update_user_stats(user,likes=0,retweets=0,bot=0):
    stats = auth.get_file(user,'stats') or {}
    stats['likes'] = stats.get('likes',0) + likes
    stats['retweets'] = stats.get('retweets',0) + retweets
    auth.set_file(user,'stats',stats)


def dotask(userdata,todo):
	from ditweets.controllers.twitter import twitterAccount
	api = twitterAccount(userdata)
	print("go")
	retweets = 0
	likes = 0



	for id in todo['like'].keys():
		try:
			api.CreateFavorite(status_id=id, include_entities=False)
			likes += 1
		except Exception as err:
			pass
			print(err.message)
		    #for i in err.message:
		    #    print(i)

	for id in todo['rt'].keys():
		try:
			sleep(random.random()/2)
			api.PostRetweet(status_id=id,trim_user=True)
			retweets += 1

		except Exception as err:
			pass
			print(err.message)
		    #for i in err.message:
		    #    print(i)

			#print(err.args[0][0]['code'])



	update_user_stats(userdata['username'],retweets=retweets,likes=likes)

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
