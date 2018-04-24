import twitter
api = twitter.Api(consumer_key='wp6z34wTKT1qEgpACclxE2mNb',
                  consumer_secret='O2UxPabL2l9cqRFbFqxkGaQZxUiu4ouKNPei2CyAcDRzDXVWJz',
                  access_token_key='3434108799-03QK2j2y4mTPThgX5a4gC33ZbURaavD8QgMsktT',
                  access_token_secret='Iznn3zJzqpHez9FKwbFrejUk23FwWhmminPx4rsvWGDqZ')

#status = api.PostUpdate('test ditweets')
user="JLMelenchon"
statuses = api.GetUserTimeline(screen_name=user)
print([s.id for s in statuses],len(statuses))
exit(0)
lastTweet=api.GetUserTimeline(screen_name=user)[0]
print(lastTweet)
print(lastTweet.id)
api.CreateFavorite(status_id=lastTweet.id)
#api.PostRetweet(lastTweet.id)
m = api.GetFriends()
#print(m)
