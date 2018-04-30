# -*- coding: utf-8 -*-

from ditweets import cache
from ditweets.auth import require_login, auth
from ditweets.tools import get_accounts_list

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
    lastId = cache.get('tweeter_last_id',0)
    lastId = 990230265426563077
    if lastId:
        params['since_id'] = lastId
    else:
        params['count'] = 1
    maxId = lastId

    for account in get_accounts_list(cache['comptes']):
        twitter_ids[account] = {'likes':api.GetFavorites(screen_name=account,**params), 'retweets':[], 'tweets':[],'replies':[]}
        maxId = max([t.id for t in twitter_ids[account]['likes']]+[maxId])
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
    return twitter_ids

import json
def twitter_job():
    twitter_ids = {}
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
        for id in todo['rt'].keys():
            try:
                api.PostRetweet(status_id=id,trim_user=True)
                retweets += 1
            except:
                pass
        for id in todo['like'].keys():
            try:
                api.CreateFavorite(status_id=id, include_entities=False)
                likes += 1
            except:
                pass
        update_user_stats(data['username'],retweets=retweets,likes=likes)
    return 'ok'

def get_user_stats():
    pass

def update_user_stats(user,likes=0,retweets=0,bot=0):
    stats = auth.get_file(user,'stats') or {}
    stats['likes'] = stats.get('likes',0) + likes
    stats['retweets'] = stats.get('retweets',0) + retweets
    auth.set_file(user,'stats',stats)
