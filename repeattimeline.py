# -*- coding: utf-8 -*-
import tweepy, urllib, json, webbrowser, time
from testkeys import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 12450802 #peoppenheimer's twitter ID
timeline = api.user_timeline(user_id = userID, count = 10)

for status in timeline:
    api.update_status(status.text)
    print('tweeted ' + status.text)
    time.sleep(10)
