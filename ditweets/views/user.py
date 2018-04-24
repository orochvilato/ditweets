# -*- coding: utf-8 -*-

from ditweets import app
from ditweets.auth import require_login

@app.route('/')
@require_login(redir='root')
def root():
    return "boom"
