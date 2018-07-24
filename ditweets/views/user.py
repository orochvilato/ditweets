# -*- coding: utf-8 -*-

from ditweets import app, cache, mdb, mdbrw
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
    return twitter_job()

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

@app.route('/action',methods=['POST','GET'])
@app.route('/action/<action_id>',methods=['POST','GET'])
@require_login('/action_tweet')
def action_tweet(action_id=None):
    if request.method=='GET':
        action = get_action(action_id) if action_id else {}
        return render_template('action.html',action_id=action_id,**action)
    elif request.method=='POST':
        action = {}
        if request.form.get('tweet_type')=='tweet':
            action.update({
                'tweet_content':request.form.get('tweet_content'),
                'tweet_medias':request.form.get('tweet_medias'),
            })
        else:
            action.update({
                'tweet_id':request.form.get('tweet_id'),
            })
        action.update({
            'tweet_tags': request.form.get('tweet_tags'),
            'start': request.form.get('start')
            })
        if request.form.get('diffusion_active')=='on':
            diff_actions = []
            if request.form.get('like'):
                diff_actions.append('like')
            if request.form.get('rt'):
                diff_actions.append('rt')

            action.update({
                'duration': request.form.get('duration'),
                'actions': diff_actions,
                'comptes': request.form.get('comptes'),
                'diffusion': request.form.get('diffusion')
            })


        data = auth.get_data(session['id']['username'])
        action_id = request.form.get('action_id')
        if 'tweet_id' in action.keys():
            api = twitterAccount(twitter_fetch)
            try:
                tweet = api.GetStatus(status_id = tweet_id)
                action['tweet_text'] = tweet.text
                action['user'] = tweet.user.name
                #<a href="https://twitter.com/statuses/{{ action['tweet_id'] }}">{{ action['tweet_text'] }}</a>
                action['screenname'] = tweet.user.screen_name
                action['user_image'] = tweet.user.profile_image_url
            except:
                return render_template('action.html', action_id=action_id, **action, tweet_error=True)

        if action_id:
            update_action(action_id,action)
        else:
            id = add_action(action)
        return request.form.get('start')

@app.route('/actions')
def view_actions():
    actions = sorted([ action for action in get_actions().values()], key=lambda x:x['start'], reverse = True)

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

@app.route('/logs')
@require_login(redir='logs')
def logs():
    username = session['id']['username']
    items = mdb.logs.find({'username':username},{'action':1,'tweet_id':1,'_id':None}).sort('tweet_id',-1)
    #import json
    #return json.dumps(list(items), sort_keys=True, indent=4)
    return render_template('logs.html',logs=items)

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

    defaults = cache['defaults']
    params = dict((k,'100' if v=='on' else v) for k,v in data.get('params',{}).items())

    return render_template('param_adv.html',session=session,defaults=defaults,comptes=cache['comptes'],params=params)

@app.route('/config')
@require_login(redir='config')
def config():
    username = session['id']['username']
    data = auth.get_data(username)
    try:
        # check twitter
        tapi = twitterAccount(data)
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
    params = dict((k,v) for k,v in request.form.to_dict().items() if v!='0')
    auth.update_data(username,{'params':params})
    return redirect('/param')

@app.route('/tops')
@require_login(redir='tops')
def tops():
    reverse = request.args.get('r',False)
    followers = {}
    for data in auth.users_data():
        followers[data['username']] = data.get('followers',0)

    pgroup = {}
    pgroup['n'] = {'$sum':1}
    pgroup['_id'] = { 'user':'$username','action':'$action'}
    pipeline = [{'$match':{'error':None}},
                {'$group':pgroup},
                {'$sort':{'n':-1}}]
    accounts = {}
    for t in mdb.logs.aggregate(pipeline):
        user = t['_id']['user']
        if not user in accounts:
            accounts[user] = dict(user=user,f=followers.get(t['_id']['user'],0),rt=0,like=0)
        accounts[user][t['_id']['action']] = t['n']

    accounts = sorted(accounts.values(),key=lambda x:x['f']*x['rt'],reverse=True if not reverse else False)

    html = "<html><body><table border='1'><thead><tr><td>#</td><td>Utilisateur</td><td>Followers</td><td>RT</td><td>Like</td><td>Impact</td></tr></thead><tbody>"
    for i,a in enumerate(accounts):
        html += "<tr><td>{i}</td><td>{user}</td><td>{f}</td><td>{rt}</td><td>{like}</td><td>{i}</td></tr>".format(i=i+1,user=a['user'],f=a['f'],rt=a['rt'],like=a['like'],i=a['f']*a['rt'])



    if 1:
        clean_logs()
        html += "</tbody></table>"
        html += "<hr/><table border='1'><thead><tr><td>#</td><td>Compte</td><td>RT</td><td>Like</td><td>Total</td></tr></thead><tbody>"

        pgroup = {}
        pgroup['n'] = {'$sum':1}
        pgroup['_id'] = { 'author':'$author.screen_name','action':'$action'}
        pipeline = [{'$match':{'error':None}},
                    {'$group':pgroup},
                    {'$sort':{'n':-1}}]
        accounts = {}
        for t in mdb.logs.aggregate(pipeline):
            sn = t['_id']['author']
            if not sn in accounts.keys():
                accounts[sn] = { 'author':t['_id']['author'],'rt':0,'like':0 }
            accounts[sn][t['_id']['action']] = t['n']

        accounts = sorted(accounts.values(),key=lambda x:x.get('rt',0)+x.get('like',0),reverse=True)
        for i,a in enumerate(accounts[:100]):
            html += '<tr><td>{i}</td><td>{user}</td><td>{rt}</td><td>{like}</td><td>{total}</td></tr>'.format(
                user='@'+a['author'],i=i+1,rt=a['rt'],like=a['like'],total=a['rt']+a['like'])




    html += "</tbody></table></body></html>"
    return html

@app.route('/tests')
def tests():
    from ditweets.controllers.twitter import twitterAccount, getTwitterData, twitter_job
    from ditweets.config_private import twitter_fetch
    from ditweets.tools import get_accounts_list

    for data in auth.users_data():
        try:
            api = twitterAccount(data)
            screen_name = api.GetUserTimeline(count=1)[0].user.screen_name
            followers = api.GetUser(screen_name=screen_name).followers_count
            auth.update_data(data['username'],{'followers':followers,'screenname':screen_name})
        except:
            pass
    return "ok"

@app.route('/corrigedate')
def corrige():
    from ditweets.controllers.twitter import cvTwitterDate
    from ditweets import mdbrw
    for t in mdb.tweets.find({},{'created_at'}):
        if isinstance(t['created_at'],str):
            mdbrw.tweets.update({'_id':t['_id']},{'$set':{'created_at':cvTwitterDate(t['created_at'])}})

@app.route('/clean_logs')
def clean_logs():
    from ditweets import mdbrw
    if 0:
        prec = []
        for t in mdb.logs.find({}).sort([('username',1),('tweet_id',1),('action',1)]):
            cur = [t['username'],t['tweet_id'],t['action']]
            if cur == prec:
                mdbrw.logs.remove({'_id':t['_id']})
            prec = cur
    tdict = {}
    for l in mdb.logs.find({'author':None},{'tweet_id':1}):
        if not l['tweet_id'] in tdict.keys():
            tdict[l['tweet_id']] = []
        if not l['_id'] in tdict[l['tweet_id']]:
            tdict[l['tweet_id']].append(l['_id'])

    upd = []
    from pymongo import UpdateOne
    for t in mdb.tweets.find({'id':{'$in':list(tdict.keys())}},{'id':1,'user':1}):
        for l_id in tdict[t['id']]:
            upd.append(UpdateOne({'_id':l_id},{'$set':{'author':t['user']}}))
    if upd:
        mdbrw.logs.bulk_write(upd)
