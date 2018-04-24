# -*- coding: utf-8 -*-

from ditweets import app
from ditweets.auth import require_login
from flask import render_template
accounts = ['Francois_Ruffin']
@app.route('/')
@require_login(redir='root')
def root():
    return render_template('main.html')
