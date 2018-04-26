#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import g, request, redirect, url_for, make_response, session, Response, render_template
from flask.views import View
from  ditweets.tools import sendmail2
import sys
import json
import os

def AUTH(app,path=''):
    app.add_url_rule(path+'/login',view_func=LoginView.as_view('login'))
    app.add_url_rule(path+'/signin',view_func=SigninView.as_view('signin'))
    app.add_url_rule(path+'/reset_request',view_func=ResetRequestView.as_view('reset_request'))
    app.add_url_rule(path+'/logout',view_func=logoutview)
    app.add_url_rule(path+'/logged',view_func=loggedview)
    app.add_url_rule(path+'/reset_password',view_func=ResetPasswordView.as_view('reset_password'))
    auth.init(app.app_path)

from diskcache import Cache
cache = Cache('/tmp/cache_ditweets')

class ResetRequestView(View):
    methods = ['GET','POST']
    def dispatch_request(self):
        if request.method=='GET':
            return render_template('reset_request.html')
        elif request.method=='POST':
            username = request.form.get('username')
            import uuid
            uid = str(uuid.uuid4())
            cache.set(uid,username,expire=360)
            data = auth.get_data(username)
            email = data['email']
            msg = u"""Pour reinitiliser votre mot de passe cliquer <a href="{url}">ici</a>""".format(url=url_for('reset_password', uid=uid, _external=True))
            if email:
                print(email)
                sendmail2("DITweets.di",email,u"Réinitialisation mot de passe",msg=msg)
                return render_template('reset_request.html', sent=True)

class ResetPasswordView(View):
    methods = ['GET','POST']
    def dispatch_request(self):
        if request.method=='GET':
            uid = request.args.get('uid',None)
            return render_template('reset_password.html', uid=uid)
        elif request.method=='POST':
            uid = request.form.get('uid')
            newpass = request.form.get('password')
            username = cache.get(uid)
            if not username:
                return json.dumps({})
            auth.set_pwd(username,newpass)
            del cache[uid]
            return redirect('/')



class SigninView(View):
    methods = ['GET','POST']
    def dispatch_request(self):
        if request.method=='GET':
            return render_template('signin.html')
        elif request.method=='POST':
            user = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email',None)
            if request.form.get('nobot').lower!='sram':
                return render_template('signin.html',boterror=True)
            if auth.create_user(user,password,email):
                session['id'] = {'username':user,'password':password}
                return redirect(url_for('login'))
            else:
                return render_template('signin.html',signinerror=True)


class LoginView(View):
    methods = ['GET','POST']
    def dispatch_request(self):
        if request.method=='GET':
            return render_template('login.html')
        elif request.method=='POST':
            user = request.form.get('username')
            password = request.form.get('password')
            #rdir = request.form.get('redirect')
            import json
            if auth.authenticate(user,password):
                session['id'] = {'username':user,'password':password}
                return redirect(url_for(session['redirect']))
            else:
                return render_template('login.html',loginerror=True)

def logoutview():
    if 'id' in session:
        del session['id']
    return redirect('/')

def loggedview():
    import json
    if 'id' in session:
        #return json.dumps(roles)
        data = auth.get_data(session['id']['username'])
        data['count'] = data.get('count',0) + 1
        auth.update_data(session['id']['username'],data)
        ret = {'username':session['id']['username'],'data':data}
        return json.dumps(ret)
    else:
        return json.dumps({})


def require_login(redir):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if 'id' in session:
                return f(*args,**kwargs)
            else:
                session['redirect'] = redir
                return redirect(url_for('login'))
        return decorated_function
    return decorator

def require_basicauth(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        m = sys.modules[f.__module__]
        rauth = request.authorization
        if not rauth or rauth.username not in m.users or not auth.authenticate(rauth.username,rauth.password):
            return Response(u'Accès protégé\nMerci de vous authentifier',401,{'WWW-Authenticate':'Basic realm="Login Required"'})
        return f(*args,**kwargs)
    return decorated_function

from passlib.hash import pbkdf2_sha256
import pickle

class Auth:
    def __init__(self):
        pass

    def exists(self,username):
        userdir = self._getdir(username)
        return os.path.exists(userdir)

    def _getdir(self,username):
        username = username.replace('/','').replace('.','').replace('?','')
        return os.path.join(self.path,username)

    def get_dir(self,username):
        userdir = self._getdir(username)
        if os.path.exists(userdir):
            return userdir
        else:
            return None
    def get_pwd(self,username):
        userdir = self.get_dir(username)
        if userdir:
            return open(os.path.join(userdir,'passwd')).read()
        else:
            return None

    def set_pwd(self,username,password):
        userdir = self.get_dir(username)
        hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        return open(os.path.join(userdir,'passwd'),'w').write(hash)

    def get_data(self,username):
        userdir = self.get_dir(username)
        return pickle.load(open(os.path.join(userdir,'data'),'rb'))

    def set_data(self,username,data):
        userdir = self.get_dir(username)
        pickle.dump(data,open(os.path.join(userdir,'data'),'wb'))

    def init(self,app_path):
        path = os.path.join(app_path,'users')
        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path

    def create_user(self,username, password, email):
        userdir = self._getdir(username)
        if not os.path.exists(userdir):
            os.makedirs(userdir)
            self.set_data(username,{'email':email})
            self.set_pwd(username,password)
            return True
        else:
            return False

    def authenticate(self,username, password):
        userdir = self._getdir(username)
        hash = self.get_pwd(username)
        if not hash or not password:
            return False
        return pbkdf2_sha256.verify(password,hash)

    def update_data(self,username,newdata):
        data = self.get_data(username)
        data.update(newdata)
        self.set_data(username,data)


auth = Auth()
