definition = dict(
    name = __name__,
    active = True,
    type = 'cron',
    params = dict(minute='*/20'),
    description = "Test",
    notify_error = ['observatoireapi@yahoo.com']
    )

from ditweets.controllers.twitter import twitter_job
from ditweets.controllers.imports import gsheet_twitter

def job(**kwargs):
    gsheet_twitter()
    twitter_job()
