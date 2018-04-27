import twitter


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
