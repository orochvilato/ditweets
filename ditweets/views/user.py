# -*- coding: utf-8 -*-

from ditweets import app, cache, accounts
from ditweets.auth import require_login, auth
from flask import render_template, request, session, redirect
import json





from ditweets.controllers.twitter import twitter_job, twitterAccount

@app.route('/test')
def test():
    username = session['id']['username']
    data = auth.get_data(username)
    # check twitter
    tapi = twitterAccount(data)
    lasttweet = tapi.GetUserTimeline(screen_name="Action_Insoumis",count=30,exclude_replies=True)
    for tweet in lasttweet:
        print(tweet.id,tweet.text)
    return "ok"
    #exclude_replies
@app.route('/forcetask')
def forcetask():
    return twitter_job()


@app.route('/')
@require_login(redir='root')
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
    return render_template('param.html',session=session,accounts=accounts,params=data.get('params',{}))

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
