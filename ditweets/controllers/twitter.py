# -*- coding: utf-8 -*-

from ditweets import cache
from ditweets.auth import require_login, auth
from ditweets.tools import get_accounts_list

from ditweets.controllers.tasks import q as qtwitter


def twitterAccount(data):
    import twitter
    api = twitter.Api(consumer_key=data.get('twitter_consumer_key','nope'),
                      consumer_secret=data.get('twitter_consumer_secret','nope'),
                      access_token_key=data.get('twitter_access_token','nope'),
                      access_token_secret=data.get('twitter_access_token_secret','nope'))
    return api


def getTwitterData(api):
    twitter_ids = {}
    # Recuperation ID Tweets, RT et Likes des comptes paramétrés
    params = {}
    paramsLike = {}
    lastId = cache.get('tweeter_last_id',0)
    lastIdLike = cache.get('tweeter_last_id_like',0)
    lastIdLike = 0
    #lastId = 992788759014985727
    if lastId:
        params['since_id'] = lastId
    else:
        params['count'] = 10
    if lastIdLike:
        paramsLike['since_id'] = lastIdLike
    else:
        paramsLike['count'] = 10



    maxId = lastId
    maxIdLike = lastIdLike

    for account in ['Deputee_Obono']: #get_accounts_list(cache['comptes']):
        # une valeur par compte
        twitter_ids[account] = {'likes':api.GetFavorites(screen_name=account,**paramsLike), 'retweets':[], 'tweets':[],'replies':[]}
        for like in twitter_ids[account]['likes']:
            print(like.id,like.created_at)
        1/0
        maxIdLike = max([t.id for t in twitter_ids[account]['likes']]+[maxIdLike])

        for tweet in api.GetUserTimeline(screen_name=account,**params):
            if tweet.in_reply_to_screen_name:
                twitter_ids[account]['replies'].append(tweet)
            elif tweet.retweeted_status:
                twitter_ids[account]['retweets'].append(tweet)
            else:
                twitter_ids[account]['tweets'].append(tweet)
            maxId = max([maxId,tweet.id])
        #except:
        #    pass
        #twitter_ids[account]['tweets'] =
        #twitter_ids[account]['retweets'] = api.GetRetweets(screen_name=account,**params)
    cache['tweeter_last_id'] = maxId
    cache['tweeter_last_id_like'] = maxIdLike

    return twitter_ids

import json
def twitter_job():
    twitter_ids = {}
    print('twitter_job')
    for data in auth.users_data():
        if not data.get('twitter_success',False):
            continue
        api = twitterAccount(data)
        if not twitter_ids:
            twitter_ids = getTwitterData(api)

        todo = {'rt':{},'like':{}}
        for account in get_accounts_list(cache['comptes']):

            actions = {'like':[],'rt':[]}
            for _item,_action in [('tweets','rt'),('tweets','like'),('retweets','rt'),('retweets','like'),('likes','rt'),('likes','like'),('replies','rt'),('replies','like')]:
                item = "{account}_{item}_{action}".format(account=account, item=_item, action=_action)
                if item in data.get('params',{}).keys():
                    actions[_action] = actions.get(_action,[]) + [ _item ]
            for do in ['rt','like']:
                for it in actions[do]:
                    for tweet in twitter_ids.get(account,{}).get(it,[]):
                        todo[do][tweet.id] = 1
        retweets = 0
        likes = 0

        qtwitter.put({'userdata':data,'todo':todo})


    return 'ok'

def get_user_stats():
    pass

def update_user_stats(user,likes=0,retweets=0,bot=0):
    stats = auth.get_file(user,'stats') or {}
    stats['likes'] = stats.get('likes',0) + likes
    stats['retweets'] = stats.get('retweets',0) + retweets
    auth.set_file(user,'stats',stats)
