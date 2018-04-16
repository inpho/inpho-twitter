from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import tweepy, time, urllib.request, urllib.parse, urllib.error, json, requests
from urllib.parse import quote
from requests import get
from bs4 import BeautifulSoup
from keys import *

#function used to add '+' in between words from the tweet
#returns title: the formal title of the article
#returns url: the title but with '+' in between
def buildURL (broken_tweet):
    title = ""
    url = ""
    for word in broken_tweet:
        title = title + word + ' '
        url = url + quote(word) + '+'
        
    title = title[:-1]
    url = url[:-1]
    return url, title;

#function used to check if the query returns more than one result
#returns true if more than one result is found
#reutrns false otherwise
def isMultiple (inpho_json):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result
        print('multiple results for same sep_dir')
        return True; #notify of error
    return False;

#function to check url is valid for responding with
    #currently checks if article is from the "school of thought" ontology
    #or if the link returns an error
#returns false if it is,
#returns true otherwise
def validUrl (url):
    try:
        check = urllib.request.urlopen('https://www.inphoproject.org' + url)
    except urllib.error.HTTPError as e:
        print('500 error') #notify of error
        return False;
    if url.split('/')[1] == 'school_of_thought':
        print(url + ' found in school of thought')
        return False;
    return True;

#function that assembles the reply tweet from the url and title
#retrieves update message from SEP RSS
#returns response: the message to be tweeted back
def createResponse (url, title):
    rss = urllib.request.urlopen('https://plato.stanford.edu/rss/sep.xml')
    soup = BeautifulSoup(rss, 'html.parser')
    response = ''
    for entry in soup.find_all('item'):
        if str(entry.title) == '<title>' + title + '</title>':
            start = str(entry.description).find('[') + 1
            end = str(entry.description).find(']')
            if start == -1 or end == -1:
                print('rss not found') #notify of error
            else:
                response = str(entry.description)[start:end]
            break;
    link = 'https://www.inphoproject.org' + url
    response = response + '\nInPhO - ' + title + ' - ' + link
    return response;

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 975141243348049921 #userID of dummy test account
myID = 974652683788455936
last_tweet = api.user_timeline(user_id = myID, count = 1)[0] #last status sent by the bot
print('last tweet was: ' + last_tweet.text)
last_reply_id = last_tweet.in_reply_to_status_id #id of the last status the bot replied to
print('with id of ' + str(last_reply_id))
timeline = api.user_timeline(user_id = userID, count = 5) #change 5 based on frequency of running bot
last_index = len(timeline)
for x in range(0, len(timeline)):    
    if timeline[x].id == last_reply_id:
        last_index = x
timeline = timeline[:last_index] #truncates tweets bot has already replied to

#timeline returns count number of tweets from specified user, in order of most recent to least recent
#reverse the order of timeline so that they are replied to in the opposite order
for i in range(len(timeline)-1, -1, -1):
    status = timeline[i]
    #first check to see if bot already replied, if it has, don't continue reading timeline
    print(status.text)
    if status.id == last_reply_id:
        print('already responded to ' + status.text)
        break;
    else:
        broken_tweet = status.text.split(" ")
        if broken_tweet[0] != 'SEP:': #tweet wasn't a SEP tweet
            print('not SEP tweet')
        else:
            del broken_tweet[0]
            del broken_tweet[len(broken_tweet)-1]
            sep_url = broken_tweet[len(broken_tweet)-1]
            del broken_tweet[len(broken_tweet)-1]

            url, title = buildURL(broken_tweet);
            
            sep_url = requests.get(sep_url).url #get redirect URL
            sep_url = sep_url.split('/')
            sep_title = sep_url[len(sep_url)-2] #get sep_dir value to search by
            url = 'https://inphoproject.org/entity.json?sep=' + sep_title + '&redirect=True'
            
            inpho_json = json.load(urllib.request.urlopen(url))
            
            if 'url' not in inpho_json: #flag for missing page
                print('page missing! couldn\'t find ' + title) #in future: post to text file? send alert?
                if not isMultiple(inpho_json):
                    print('!!!!!!!!!!!!!!!!!!!!!!!could not find!!!!!!!!!!!!!!!!!!!!!!!')
            else:
                if validUrl(inpho_json['url']):
                    response = createResponse(inpho_json['url'], title)

    #                   time.sleep(60) #change later to be variable 60-600
                    api.update_status('@nesscoli ' + response, status.id)
                    print('tweet response: ' + response + ' to: ' + status.text)


