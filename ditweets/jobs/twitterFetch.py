definition = dict(
    name = __name__,
    active = True,
    type = 'cron',
    params = dict(minute='*/30'),
    description = "Test",
    notify_error = ['observatoireapi@yahoo.com']
    )

from ditweets.controllers.imports import gsheet_twitter
from ditweets.controllers.twitter import twitterAccount, getTwitterData, twitter_job
from ditweets.config_private import twitter_fetch


def job(**kwargs):
    gsheet_twitter()
    api = twitterAccount(twitter_fetch)
    getTwitterData(api)
