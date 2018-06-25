definition = dict(
    name = __name__,
    active = False,
    type = 'cron',
    params = dict(hour='1'),
    description = "FollowerCount",
    notify_error = ['observatoireapi@yahoo.com']
    )

from ditweets import cache
from ditweets.controllers.imports import gsheet_twitter
from ditweets.controllers.twitter import twitterAccount, getTwitterData, twitter_job
from ditweets.config_private import twitter_fetch
from ditweets.tools import get_accounts_list

def job(**kwargs):
    api = twitterAccount(twitter_fetch)

    for account in get_accounts_list(cache['comptes']):
        pass
        #api.GetUser(screen_name=)
    twitter_job()
