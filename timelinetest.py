import tweepy, urllib, json
from keys import *
#from bot import buildURL, lookUp, createResponse #not working, need to fix

#function used to add '+' in between words from the tweet
#returns title: the formal title of the article
#returns url: the title but with '+' in between
def buildURL (broken_tweet):
    title = ""
    url = ""
    for word in broken_tweet:
        title = title + word + ' '
        url = url + word + '+'
        
    title = title[:-1]
    url = url[:-1]
    return url, title;

#function used to check for results from a particular url search
#returns true if at least one result was found
    #note that if >1 is found, the first result is chosen
#returns false otherwise
def lookUp (url):
    print('searching for: ' + url + ' instead')
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.urlopen(url))

    if 'url' not in inpho_json: #could be missing OR have 2+ results
        resDat = inpho_json.get('responseData')
        res = resDat.get('results')
        if len(res) > 0: #there was >1 result. choose 1st result
            url = res[0].get('url')
            response = createResponse(url, title)
            return True;
        else: #no results at all
            print('page is missing')
    else: #1 result found
        response = createResponse(inpho_json['url'], title)
        return True;
    return False;

#function that assembles the reply tweet from the url and title
#returns response: the message to be tweeted back
def createResponse (url, title):
    link = 'https://www.inphoproject.org' + url
    response = 'InPhO - ' + title + ' - ' + link
    print(response)
    return response;


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 12450802 #peoppenheimer's twitter ID
print('testing')
timeline = api.user_timeline(user_id = userID, count = 10)

for status in timeline:
    broken_tweet = status.text.split(" ")
    if broken_tweet[0] != 'SEP:': #tweet wasn't a SEP tweet
        print('not SEP tweet')
        exit()
    del broken_tweet[0]
    del broken_tweet[len(broken_tweet)-1]
    del broken_tweet[len(broken_tweet)-1]

    url, title = buildURL(broken_tweet);
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.urlopen(url))
    
    if 'url' not in inpho_json: #flag for missing page
            print('page missing! couldn\'t find ' + title) #in future: post to text file? send alert?

            #now, remove one "extra" word at a time (articles, conjunctions)
            for word in broken_tweet:
                if word.lower() == 'the' or word.lower() == 'of' or word.lower() == 'a' or \
                   word.lower() == 'an' or word.lower() == 'for' or word.lower() == 'and' or \
                   word.lower() == 'but' or word.lower() == 'or' or word.lower() == 'yet':
                    print('removed article: ' + word)
                    broken_tweet.remove(word)
                    url, temp = buildURL(broken_tweet)
                    if lookUp(url): #try to find page each time a word is removed
                        break;
    else:
        response = createResponse(inpho_json['url'], title)