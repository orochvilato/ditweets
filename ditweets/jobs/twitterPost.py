definition = dict(
    name = __name__,
    active = True,
    type = 'interval',
    params = dict(seconds=120),
    description = "Test",
    notify_error = ['observatoireapi@yahoo.com']
    )

from ditweets.controllers.imports import gsheet_twitter
from ditweets.controllers.twitter import twitterAccount, getTwitterData, twitter_job
from ditweets.config_private import twitter_fetch
from ditweets import jobs
from random import randint
def job(**kwargs):
    #open('/tmp/test','a').write('ok\n')
    twitter_job()
    jobs.scheduler.reschedule_job(__name__, trigger='interval', seconds=randint(120,420))
