# -*- coding: utf-8 -*-

from ditweets import app, cache
from ditweets.auth import require_login, auth, is_admin
from flask import render_template, request, session, redirect
import json




from ditweets.controllers.twitter import twitter_job, twitterAccount
from ditweets.controllers.imports import gsheet_twitter
@app.route('/forcereload')
@is_admin
def forcereload():
    gsheet_twitter()
    return redirect('/')

@app.route('/stats')
@require_login(redir='stats')
def stats():
    username = session['id']['username']
    data = auth.get_file(username,'stats')
    print(data)
    return "ok"

@app.route('/forcetask')
@is_admin
def forcetask():
    twitter_job()
    return redirect('/')

from ditweets.controllers.twitter import twitterAccount, getTwitterData, twitter_job
from ditweets.config_private import twitter_fetch
@app.route('/newt')
def newt():
    #api = twitterAccount(twitter_fetch)
    #getTwitterData(api)
    twitter_job()

from ditweets.controllers.actions import add_action, del_action, update_action, get_action, get_actions


@app.route('/queue')
def test_queue():
    from ditweets.controllers.tasks import q
    import random
    for j in range(100):
        id = "%02d" % j
        for i,a in enumerate(range(random.randrange(1,10))):
            q.put({'id':id,'item':i})


@app.route('/del_action/<action_id>')
def view_del_action(action_id):
    del_action(action_id)
    return redirect('/actions')

@app.route('/tweet_edit', methods=['POST','GET'])
def edit_tweet(tweet_id=None):
    return render_template('tweet_edit.html')

@app.route('/action_tweet',methods=['POST','GET'])
@app.route('/action_tweet/<action_id>',methods=['POST','GET'])
@require_login('/action_tweet')
def action_tweet(action_id=None):
    if request.method=='GET':
        action = get_action(action_id) if action_id else {}
        return render_template('action.html',action_id=action_id,**action)
    elif request.method=='POST':
        actions = []
        if request.form.get('like'):
            actions.append('like')
        if request.form.get('rt'):
            actions.append('rt')
        tweet_id = request.form.get('tweet_id')
        action = {'duration': int(request.form.get('duration')),
                'actions': actions,
              'tweet_id': tweet_id,
              'number': int(request.form.get('number')),
              'start': request.form.get('start')
              }
        data = auth.get_data(session['id']['username'])
        api = twitterAccount(data)
        action_id = request.form.get('action_id')
        try:
            tweet = api.GetStatus(status_id = tweet_id)
            action['tweet_text'] = tweet.text
            action['user'] = tweet.user.name
            #<a href="https://twitter.com/statuses/{{ action['tweet_id'] }}">{{ action['tweet_text'] }}</a>
            action['screenname'] = tweet.user.screen_name
            action['user_image'] = tweet.user.profile_image_url
            if action_id:
                update_action(action_id,action)
            else:
                id = add_action(action)
            return redirect('/actions')
        except:
            return render_template('action_tweet.html', action_id=action_id, **action, tweet_error=True)

@app.route('/actions')
def view_actions():
    actions = sorted([ action for action in get_actions().values()], key=lambda x:x['start'], reverse = True)
    print(actions)
    return render_template('actions.html', actions=actions)

@app.route('/test')
def test():
    username = session['id']['username']
    data = auth.get_data(username)
    # check twitter
    tapi = twitterAccount(data)
    tweets = tapi.GetUserTimeline(screen_name="Action_Insoumis",count=30)
    for t in tweets:

            print(t)
        #if t.id == 990346844218757120:
        #    print(t)
    return "ok"

@app.route('/')
@require_login(redir='')
def root():
    username = session['id']['username']
    data = auth.get_data(username)
    if data.get('twitter_success',False):
        return redirect('/param')
    else:
        return redirect('config')

@app.route('/param')
@require_login(redir='param')
def param():
    username = session['id']['username']
    data = auth.get_data(username)
    return render_template('param.html',session=session,comptes=cache['comptes'],params=data.get('params',{}))

@app.route('/config')
@require_login(redir='config')
def config():
    username = session['id']['username']
    data = auth.get_data(username)
    # check twitter
    tapi = twitterAccount(data)
    try:
        lasttweet = tapi.GetUserTimeline(count=1)
        data['twitter_success'] = True
    except:
        data['twitter_success'] = False

    auth.update_data(username,{'twitter_success':data['twitter_success']})

    return render_template('config.html',**data)

@app.route('/config_twitter', methods=["POST"])
@require_login(redir='config')
def config_twitter():
    username = session['id']['username']
    data = auth.get_data(username)


    twitter_config = {'twitter_consumer_secret': request.form.get('twitter_consumer_secret'),
                      'twitter_access_token_secret': request.form.get('twitter_access_token_secret'),
                      'twitter_consumer_key': request.form.get('twitter_consumer_key'),
                      'twitter_access_token': request.form.get('twitter_access_token')}
    auth.update_data(username,twitter_config)
    return redirect('/config')

@app.route('/params', methods=["POST"])
@require_login(redir='/')
def params():
    username = session['id']['username']
    data = auth.get_data(username)
    auth.update_data(username,{'params':request.form.to_dict()})
    return redirect('/param')
