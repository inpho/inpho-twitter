# -*- coding: utf-8 -*-
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import tweepy, urllib.request, urllib.parse, urllib.error, json, webbrowser, requests
from urllib.parse import quote
from requests import get
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
        url = url + quote(word) + '+'
        
    title = title[:-1]
    url = url[:-1]
    return url, title;

#function used to check for results from a particular url search
#returns true if at least one result was found
    #note that if >1 is found, the first result is chosen
#returns false otherwise
def lookUp (url):
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.request.urlopen(url))

    if 'url' not in inpho_json: #could be missing OR have 2+ results
        if isMultiple(inpho_json):
            return True;
    else: #1 result found
        if validUrl(inpho_json['url']):
            response = createResponse(inpho_json['url'], title)
            return True;
    return False;

#function used to check for results from a last name only search
#returns true if at least one result was found
    #note that if >1 is found, the first result is chosen
#returns false otherwise
def lookUp_lastName(url):
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.request.urlopen(url))

    if 'url' not in inpho_json: #could be missing OR have 2+ results
        resDat = inpho_json.get('responseData')
        res = resDat.get('results')
        if len(res) > 0: #there was >1 result. choose 1st result
            url = res[0].get('url')
            if res[0].get('type') == 'thinker':
                f.write('found >1 result and chose 1st option, by searching for last name.')
                response = createResponse(url, title)
                return True;
    else:
        if inpho_json['type'] == 'thinker':
            response = createResponse(inpho_json['url'], title)
            return True;
    return False;
            
#function used to check if the query returns more than one result
#returns true if more than one result is found
    #note that the first result is chosen for the response
#reutrns false otherwise
def isMultiple (inpho_json, title):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result. choose 1st result
        for entry in res:
            if entry.get('label') == title: #compare with label
                url = entry.get('url')
        if validUrl(url):
            f.write('found >1 result and chose the correct match')
            response = createResponse(url, title)
            return True;
    return False;

#function that assembles the reply tweet from the url and title
#returns response: the message to be tweeted back
def createResponse (url, title):
    link = 'https://www.inphoproject.org' + url
#    webbrowser.open(link, new=2) #opens link in new tab of default browser
    response = 'InPhO - ' + title + ' - ' + link
    l.write(link)
    l.write('\n')
    print(response)
    return response;

#function to check url is valid for responding with
    #currently checks if article is from the "school of thought" ontology
#returns false if it is,
#returns true otherwise
def validUrl (url):
    if url.split('/')[0] == 'school_of_thought':
        f.write('found in school of thought')
        return False;
    return True;

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 12450802 #peoppenheimer's twitter ID
timeline = api.user_timeline(user_id = userID, count = 100)
i = 0
f = open('results.txt', 'w')
l = open('links.txt', 'w')
m = open('multLinks.txt', 'w')
for status in timeline:
    broken_tweet = status.text.split(" ")

    if broken_tweet[0] != 'SEP:': #tweet wasn't a SEP tweet
        print('not SEP tweet')
        continue;
    del broken_tweet[0]
    del broken_tweet[len(broken_tweet)-1]
    sep_url = broken_tweet[len(broken_tweet)-1]
    del broken_tweet[len(broken_tweet)-1]
    i = i + 1
    print(i)
    url, title = buildURL(broken_tweet)
    
    f.write('\n' + str(title.encode('utf8')) + ': ')
 #   url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
 
    sep_url = requests.get(sep_url).url
    sep_url = sep_url.split('/')
    sep_title = sep_url[len(sep_url)-2]
    url = 'https://inphoproject.org/entity.json?sep=' + sep_title + '&redirect=True'
    
    inpho_json = json.load(urllib.request.urlopen(url))
    
    
    if 'url' not in inpho_json: #flag for missing page
        if not isMultiple(inpho_json, title): 
            found = False
            #now, remove one "extra" word at a time (articles, conjunctions)
            for word in broken_tweet:
                if word.lower() == 'the' or word.lower() == 'of' or word.lower() == 'a' or \
                    word.lower() == 'an' or word.lower() == 'for' or word.lower() == 'and' or \
                    word.lower() == 'but' or word.lower() == 'or' or word.lower() == 'yet':
                    broken_tweet.remove(word)
                    url, temp = buildURL(broken_tweet)
                    found = lookUp(url) #try to find page each time a word is removed
                    if found:
                        f.write('found after removing an article(s)')
                        break;
            if not found: #removing articles did not help.
                lastWord = broken_tweet[len(broken_tweet)-1]
                if lastWord[len(lastWord)-1] == 's':
                    lastWord = broken_tweet[len(broken_tweet)-1]
                    broken_tweet[len(broken_tweet)-1] = lastWord[:len(lastWord)-1]
                    url, temp = buildURL(broken_tweet)
                    found = lookUp(url)
                    if found:
                        f.write('found by removing last word plural')
                if not found:
                    found = lookUp_lastName(lastWord)
                    if found:
                        f.write('found by searching by last name')
                    else:
                        f.write('!!!!!!!!!!!!!!!!!!!!!!!could not find!!!!!!!!!!!!!!!!!!!!!!!')
    else:
        if validUrl(inpho_json['url']):
            f.write('found on first try')
            response = createResponse(inpho_json['url'], title)

f.close()
l.close()
m.close()
