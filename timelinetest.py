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
           
#function used to check if the query returns more than one result
#returns true if more than one result is found
    #if true, also calls createResponse with the matching result, based on comparing
    #label value from json with the title from the tweet
#reutrns false otherwise
def isMultiple (inpho_json):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result
        return True; #notify of error
##        for entry in res:
##            if entry.get('label') == title: #compare label with title
##                url = entry.get('url')
##        if validUrl(url):
##            f.write('found >1 result and chose the correct match')
##            response = createResponse(url, title)
##            return True;
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
        f.write('found in school of thought')
        return False;
    return True;

#function that assembles the reply tweet from the url and title
#returns response: the message to be tweeted back
def createResponse (url, title):
    link = 'https://www.inphoproject.org' + url
    response = 'InPhO - ' + title + ' - ' + link
    l.write(link)
    l.write('\n')
    print(response)
    return response;


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

userID = 12450802 #peoppenheimer's twitter ID
timeline = api.user_timeline(user_id = userID, count = 15)
i = 0
f = open('results.txt', 'w')
l = open('links.txt', 'w')

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
    print(i) #visualization of process
    
    url, title = buildURL(broken_tweet)
    f.write('\n' + str(title.encode('utf8')) + ': ') #encode unicode to be able to write to file

    sep_url = requests.get(sep_url).url #get redirect URL
    sep_url = sep_url.split('/')
    sep_title = sep_url[len(sep_url)-2] #get sep_dir value to search by
    url = 'https://inphoproject.org/entity.json?sep=' + sep_title + '&redirect=True'
    
    inpho_json = json.load(urllib.request.urlopen(url))
    
    
    if 'url' not in inpho_json: #flag for missing page
        if not isMultiple(inpho_json):
            f.write('!!!!!!!!!!!!!!!!!!!!!!!could not find!!!!!!!!!!!!!!!!!!!!!!!')
    else:
        if validUrl(inpho_json['url']):
            f.write('found on first try')
            response = createResponse(inpho_json['url'], title)

f.close()
l.close()
