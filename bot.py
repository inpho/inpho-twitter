import tweepy, time, urllib, json
from keys import *

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        broken_tweet = status.text.split(" ")
        del broken_tweet[0]
        del broken_tweet[len(broken_tweet)-1]
        del broken_tweet[len(broken_tweet)-1]

        title = ""
        url = ""
        for word in broken_tweet:
            title = title + word + ' '
            url = url + word + '+'
            
        title = title[:-1]
        url = url[:-1]
        #url containing json data for the search query of the title
        url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
        
        inpho_json = json.load(urllib.urlopen(url))
        
        #TO DO: act accordingly in response to page not being found.
        if inpho_json['responseDetails'] == None: #flag for missing page
            print('page missing! couldn\'t find ' + title) #in future: post to text file? send alert?
            
        else:
            link = 'https://www.inphoproject.org' + inpho_json['url']
        
            response = 'InPhO - ' + title + ' - ' + link

            time.sleep(60) #change later to be variable 60-600
            api.update_status('@nesscoli ' + response, status.id)
            print('tweet response: ' + response + ' to: ' + status.text)
        
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 975141243348049921 #userID of dummy test account

streamListener = MyStreamListener()
stream = tweepy.Stream(auth, streamListener)
stream.filter(follow=[str(userID)]) #returns current tweets from specified user
