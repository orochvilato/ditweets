#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import g, request, redirect, url_for, make_response, session, Response
import sys
import json
import os

def AUTH(app,path=''):
    app.add_url_rule(path+'/login',view_func=loginview)
    app.add_url_rule(path+'/logout',view_func=logoutview)
    app.add_url_rule(path+'/logged',view_func=loggedview)
    app.add_url_rule(path+'/reset_password',view_func=reset_passwordview)
    auth.init(app.app_path)

from diskcache import Cache
cache = Cache('/tmp/cache_ditweets')

def reset_passwordview():
    import uuid
    uid = str(uuid.uuid4())
    username = request.args.get('username')
    method = request.args.get('method')
    print(request.method)
    if method=='POST':
        newpass = request.args.get('password')
        uid = request.args.get('uid')
        username = cache.get(uid)
        if not username:
            return json.dumps({})
        auth.set_pwd(username,newpass)
        del cache[uid]
        return json.dumps({'username':username})
    else:
        cache.set(uid,username,expire=360)
        return uid


def loginview():
    user = request.args.get('username')
    password = request.args.get('password')
    import json
    if auth.authenticate(user,password):
        session['id'] = {'username':user,'password':password}
        return json.dumps({'username':user})
    else:
        return json.dumps({}), 401

def logoutview():
    if 'id' in session:
        del session['id']
    return json.dumps({'result':"logout"})

def loggedview():
    import json
    if 'id' in session:
        #return json.dumps(roles)
        print(session['id']['username'])
        data = auth.get_data(session['id']['username'])
        print(data)
        data['count'] = data.get('count',0) + 1
        auth.update_data(session['id']['username'],data)
        ret = {'username':session['id']['username'],'data':data}
        return json.dumps(ret)
    else:
        return json.dumps({})


def require_login(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'id' in session:
            return f(*args,**kwargs)
        return "nope",401
    return decorated_function

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


    def authenticate(self,username, password):
        userdir = self._getdir(username)
        if not os.path.exists(userdir):
            os.makedirs(userdir)
            self.set_data(username,{})
            self.set_pwd(username,password)
            return True

        hash = self.get_pwd(username)
        return pbkdf2_sha256.verify(password,hash)



    def update_data(self,username,newdata):
        data = self.get_data(username)
        data.update(newdata)
        self.set_data(username,data)


auth = Auth()
