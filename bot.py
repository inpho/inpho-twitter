import tweepy, time
from keys import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

#if specific user tweets, get tweet id, respond to tweet

#userID of dummy test account
userID = 975141243348049921

public_tweets = api.home_timeline()
for tweet in public_tweets:

    if tweet.user.id == userID:
        api.update_status('@nesscoli test response', tweet.id)
        print('tweet success!')
