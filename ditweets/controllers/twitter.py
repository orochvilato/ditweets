# -*- coding: utf-8 -*-
from ditweets import cache,accounts
from ditweets.auth import require_login, auth

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
    params = {exclude_replies=True}
    lastId = cache.get('tweeter_last_id',0)
    if lastId:
        params['since_id'] = lastId
    else:
        params['count'] = 1
    maxId = lastId
    for account in accounts:
        try:
            twitter_ids[account] = {'likes':api.GetFavorites(screen_name=account,**params), 'retweets':[], 'tweets':[]}
            maxId = max([t.id for t in twitter_ids[account]['likes']]+[maxId])
            for tweet in api.GetUserTimeline(screen_name=account,**params):
                if tweet.retweeted_status:
                    twitter_ids[account]['retweets'].append(tweet)
                else:
                    twitter_ids[account]['tweets'].append(tweet)
                maxId = max([maxId,tweet.id])
        except:
            pass
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
        for account in accounts:
            actions = {'like':[],'rt':[]}
            for _item,_action in [('tweets','rt'),('tweets','like'),('retweets','rt'),('retweets','like'),('likes','rt'),('likes','like')]:
                item = "{account}_{item}_{action}".format(account=account, item=_item, action=_action)
                if item in data.get('params',{}).keys():
                    actions[_action] = actions.get(_action,[]) + [ _item ]
            for do in ['rt','like']:
                for it in actions[do]:
                    for tweet in twitter_ids.get(account,{}).get(it,[]):
                        todo[do][tweet.id] = 1

        for id in todo['rt'].keys():
            try:
                api.PostRetweet(status_id=id,trim_user=True)
            except:
                pass
        for id in todo['like'].keys():
            try:
                api.CreateFavorite(status_id=id, include_entities=False)
            except:
                pass
    return 'ok'
