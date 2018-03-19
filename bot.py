import tweepy, time
from keys import *

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status)
        time.sleep(60) #change later to be variable 60-600
        api.update_status('@nesscoli test response', status.id)
        print(status.text)
        
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)


userID = 975141243348049921 #userID of dummy test account

streamListener = MyStreamListener()
stream = tweepy.Stream(auth, streamListener)
stream.filter(follow=[str(userID)]) #returns current tweets from specified user

#old test code: this searched through timeline for user's
#tweet to respond to. Effective but not right solution

##public_tweets = api.home_timeline()
##for tweet in public_tweets:
##
##    if tweet.user.id == userID:
##        #should check that we haven't already responded
##        time.sleep(60) #change later to be variable 60-600
###        api.update_status('@nesscoli test response', tweet.id)
##        print(tweet)
