# -*- coding: utf-8 -*-

from ditweets import app
from ditweets.auth import require_login, auth, session, redirect
from flask import render_template, request
import json

accounts = ['Francois_Ruffin',"InstantEnCommun","Action_Insoumis",'worldtvdesinfo','InstitutOPIF','LeMediaTV','LaFranceInsoumise']


@app.route('/check')
def check():
    pass
    
def twitterAccount():
    import twitter
    username = session['id']['username']
    data = auth.get_data(username)

    api = twitter.Api(consumer_key=data.get('twitter_consumer_key','nope'),
                      consumer_secret=data.get('twitter_consumer_secret','nope'),
                      access_token_key=data.get('twitter_access_token','nope'),
                      access_token_secret=data.get('twitter_access_token_secret','nope'))
    return api

@app.route('/')
@require_login(redir='root')
def root():
    username = session['id']['username']
    data = auth.get_data(username)
    return render_template('main.html',session=session,accounts=accounts,params=data.get('params',{}))

@app.route('/config')
@require_login(redir='config')
def config():
    username = session['id']['username']
    data = auth.get_data(username)
    # check twitter
    tapi = twitterAccount()
    try:
        lasttweet = tapi.GetUserTimeline(count=1)
        twitter_success = True
    except:
        twitter_success = False

    return render_template('config.html',twitter_success=twitter_success,**data)

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
    return redirect('/')
