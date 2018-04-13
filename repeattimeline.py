# -*- coding: utf-8 -*-
import tweepy, urllib, json, webbrowser, time
from testkeys import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 12450802 #peoppenheimer's twitter ID
#userID = 975141243348049921
timeline = api.user_timeline(user_id = userID, count = 5)

##for i in range(len(timeline)-1, -1, -1):
##    api.update_status(timeline[i].text)
##    print('tweeted ' + timeline[i].text)
##    time.sleep(60)
api.update_status(timeline[0].text)
