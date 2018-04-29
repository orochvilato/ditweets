# -*- coding: utf-8 -*-

from .config_private import smtp,privatekey

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

from .auth import AUTH,require_login
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import os.path
#@Action_Insoumis @InstantEnCommun @Obs_Democratie @RadioInsoumise  @LAEC_fr @Fiscal_Kombat ‏@FAQdeLAEC ‏@elonmusk @Macroverdose @worldtvdesinfo @InstitutOPIF @le_firagot @LeDeconex ‏@GocheOuDrouate ‏@melenshack @postbadjeanluc#5511 ‏@RuffinDebout ‏@Fakir_ ‏@PicardieDebout ‏@LeMediaTV @InsoumisJeunes  @FranceInsoumise ‏ @JLMelenchon
accounts = ['Francois_Ruffin',"InstantEnCommun","Action_Insoumis",'worldtvdesinfo','InstitutOPIF','LeMediaTV']

app.secret_key = privatekey
app.app_path = '/'.join(os.path.abspath(__file__).split('/')[:-2])
AUTH(app)

from diskcache import Cache
cache = Cache('/tmp/cache_ditweets')

from ditweets.controllers.imports import gsheet_twitter
gsheet_twitter()


@app.route('/testerror')
def testerror():
    1/0

if 1: #enable_logging
    import logging
    from io import StringIO
    from logging.handlers import SMTPHandler
    from logging import StreamHandler,Formatter
    import os
    import inspect
    # os.path.realpath(__file__)

    class eaiHandler(StreamHandler):
        def emit(self,record):
            StreamHandler.emit(self,record)

    class eaiSMTPHandler(SMTPHandler):
        def getSubject(self,record):
            return "Erreur Snapgen: %s (%s)" % (record.message,str(record.exc_info[:-1][1]))

    class eaiContextFilter(logging.Filter):
        def filter(self,record):
            #record.user = session['id']['username'] if 'id' in session else ''
            record.context = str(inspect.trace()[-1][0].f_locals)
            return True

    eai_handler = eaiHandler(StringIO())
    mail_handler = eaiSMTPHandler((smtp['host'],smtp['port']),
                               'api@snapgen.orvdev.fr',
                               'observatoireapi@yahoo.com', 'Erreur Snapgen',credentials=(smtp['username'],smtp['password']),secure=(None,None))

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Context:

%(context)s

Message:

%(message)s
'''))
    app.logger.addFilter(eaiContextFilter())
    app.logger.addHandler(mail_handler)
    app.logger.addHandler(eai_handler)

# Scheduler
from ditweets import jobs
jobs.start_scheduler()



from .views import user
