# -*- coding: utf-8 -*-

from ditweets import cache,mdb, mdbrw
from ditweets.auth import require_login, auth
from ditweets.tools import get_accounts_list

from ditweets.controllers.tasks import q as qtwitter
from ditweets.config_private import twitter_fetch
from ditweets.config import between_tweets_delay

def twitterAccount(data):
    import twitter
    api = twitter.Api(consumer_key=data.get('twitter_consumer_key','nope'),
                      consumer_secret=data.get('twitter_consumer_secret','nope'),
                      access_token_key=data.get('twitter_access_token','nope'),
                      access_token_secret=data.get('twitter_access_token_secret','nope'),
                      sleep_on_rate_limit=True)
    return api

def cvTwitterDate(date):
    import locale
    import datetime

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    import pytz
    return datetime.datetime.strptime(date,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)

def maxs():
    aggr = [
        {'$match': {'action':'tweet'}},
        {'$group':
          {
            '_id': "$screen_name",
            'tweet_id': { "$max": "$tweet_id" }
          }
        }
    ]
    from ditweets import mdb
    lasttweets = {}
    for a in mdb.actions.aggregate(aggr):
        for t in mdb.tweets.find({ 'id':a['tweet_id']},{'_id':None, 'created_at':1 }):
            lasttweets[a['_id']] = t['created_at']

    return(lasttweets)


def getTweet(item):

    return {
        'id':item.id,
        'created_at':cvTwitterDate(item.created_at),
        'user':{
            'screen_name':item.user.screen_name,
            'name':item.user.name,
            'profile_image_url':item.user.profile_image_url
        },

        'text':item.text,
     }

def getMaxId():
    maxId = mdb.tweets.find().sort("id",-1).limit(1)
    return maxId[0]['id'] if maxId else 0

def getTwitterData(api):
    params = {}
    import datetime, timezone
    
    lasttweets = maxs()
    for account in get_accounts_list(cache['comptes']):
        maxId = list(mdb.tweets.find({'user.screen_name': account}).sort("id",-1).limit(1))

        if maxId:
            maxId = maxId[0]['id']
            params = {'since_id': maxId}
        else:
            params = {'count': 10}

        # likes
        likes = api.GetFavorites(screen_name=account, **params)
        like_ids = []
        for like in likes:
            like_ids.append(like.id)
            tweet = getTweet(like)
            mdbrw.tweets.update({'id':like.id},{'$setOnInsert':tweet},upsert=True)
        if like_ids:
            mdbrw.actions.insert_many([dict(screen_name=account,action='like',tweet_id=id) for id in like_ids])
        items = []
        for tweet in api.GetUserTimeline(screen_name=account, **params):
            tw = getTweet(tweet)
            print(account,tw)
            mdbrw.tweets.update({'id':tweet.id},{'$setOnInsert':tw}, upsert=True)
            if tweet.in_reply_to_screen_name:
                action = "reply"
            elif tweet.retweeted_status:
                action = "retweet"
            else:
                action = "tweet"
            print(lasttweets.get(accout,'Nope'))
            if action == 'tweet' and (tw['created_at']-lasttweets.get(account,datetime.datetime(2018,1,1,tzinfo=timezone.utc))).seconds>between_tweets_delay:
                items.append(dict(screen_name=account,action=action, tweet_id=tweet.id))
            else:
                print('skipped',tw['id'])
        if items:
            mdbrw.actions.insert_many(items)
    return "ok"

import json
def twitter_job():
    maxId = mdb.logs.find().sort("tweet_id",-1).limit(1)
    maxId = maxId[0]['tweet_id'] if maxId else 0

    mdbrw.actions.update_many({'tweet_id':{'$lte':maxId}},{'$set':{'done':True}})
    twitter_ids = {}
    logs = []
    for a in mdb.actions.find({'done':None}):
        if not a['screen_name'] in twitter_ids.keys():
            twitter_ids[a['screen_name']] = {'tweets':[],'replies':[],'likes':[],'retweets':[]}
        #mdbrw.actions.update({'_id':a['_id']},{'$set':{'tweet_id':a['tweed_id']},'$unset':{'tweed_id':0}})
        if a['action']=='reply':
            twitter_ids[a['screen_name']]['replies'].append(a['tweet_id'])
        elif a['action']=='like':
            twitter_ids[a['screen_name']]['likes'].append(a['tweet_id'])
        elif a['action']=='tweet':
            twitter_ids[a['screen_name']]['tweets'].append(a['tweet_id'])
        elif a['action']=='retweet':
            twitter_ids[a['screen_name']]['retweets'].append(a['tweet_id'])

    from random import random
    for data in auth.users_data():
        if not data.get('twitter_success',False):
            continue

        todo = {'rt':{},'like':{}}
        for account in get_accounts_list(cache['comptes']):

            actions = {'like':[],'rt':[]}
            for _item,_action in [('tweets','rt'),('tweets','like'),('retweets','rt'),('retweets','like'),('likes','rt'),('likes','like'),('replies','rt'),('replies','like')]:
                item = "{account}_{item}_{action}".format(account=account, item=_item, action=_action)
                if item in data.get('params',{}).keys():
                    val = "100" if data['params'][item]=='on' else 0 if data['params'][item] in (None,'off') else data['params'][item]
                    try:
                        val = float(val)
                    except:
                        val = 0
                    if (val/100+random())>=1:
                        actions[_action] = actions.get(_action,[]) + [ _item ]
            for do in ['rt','like']:
                for it in actions[do]:
                    for tweet in twitter_ids.get(account,{}).get(it,[]):
                        todo[do][tweet] = 1

        qtwitter.put({'userdata':data,'todo':todo})

    import json
    return json.dumps(logs)

def get_user_stats():
    pass

def update_user_stats(user,likes=0,retweets=0,bot=0):
    stats = auth.get_file(user,'stats') or {}
    stats['likes'] = stats.get('likes',0) + likes
    stats['retweets'] = stats.get('retweets',0) + retweets
    auth.set_file(user,'stats',stats)
