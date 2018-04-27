definition = dict(
    name = __name__,
    active = True,
    type = 'cron',
    params = dict(minute=5),
    description = "Test",
    notify_error = ['observatoireapi@yahoo.com']
    )

from ditweets.controllers.twitter import twitter_job

def job(**kwargs):
    print(twitter_job())
