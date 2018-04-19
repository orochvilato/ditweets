definition = dict(
    name = __name__,
    active = True,
    type = 'cron',
    params = dict(minute=15),
    description = "Test",
    notify_error = ['observatoireapi@yahoo.com']
    )

def job(**kwargs):
    print('job')
