from __future__ import print_function
import urllib.request, urllib.parse, urllib.error, json
from urllib.parse import quote

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
    print(('searching for: ' + url + ' instead'))
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.request.urlopen(url))
    print(inpho_json)

    if 'url' not in inpho_json: #could be missing OR have 2+ results
        if isMultiple(inpho_json):
            return True;
        else: #no results at all
            print('page is missing')
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
def isMultiple (inpho_json):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result. choose 1st result
        url = res[0].get('url')
        if validUrl(url):
            print('found >1 result and chose 1st option')
            response = createResponse(url, title)
            return True;
    return False;

#function that assembles the reply tweet from the url and title
#returns response: the message to be tweeted back
def createResponse (url, title):
    link = 'https://www.inphoproject.org' + url
    response = 'InPhO - ' + title + ' - ' + link
    print(response)
    return response;

#function to check url is valid for responding with
    #currently checks if article is from the "school of thought" ontology
#returns false if it is,
#returns true otherwise
def validUrl (url):
    if url.split('/')[0] == 'school_of_thought':
        print('found in school of thought')
        return False;
    return True;

#############################################################################
full_tweet = "SEP: Time Travel http://ift.tt/2nhKsKL #philosophy"

broken_tweet = full_tweet.split(" ")
if broken_tweet[0] != 'SEP:': #tweet wasn't a SEP tweet
    print('not valid tweet')
    exit(); #too forceful
del broken_tweet[0]
del broken_tweet[len(broken_tweet)-1]
del broken_tweet[len(broken_tweet)-1]

url, title = buildURL(broken_tweet);

#this is the url used to extract the json data
url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url

#this next line opens the url and reads the json data
inpho_json = json.load(urllib.request.urlopen(url))

if 'url' not in inpho_json:
    #page was not found by searching the title
    if not isMultiple(inpho_json):
        found = False
        #now, remove one "extra" word at a time (articles, conjunctions)
        for word in broken_tweet:
            if word.lower() == 'the' or word.lower() == 'of' or word.lower() == 'a' or \
               word.lower() == 'an' or word.lower() == 'for' or word.lower() == 'and' or \
               word.lower() == 'but' or word.lower() == 'or' or word.lower() == 'yet':
                print(('removed article: ' + word))
                broken_tweet.remove(word)
                url, temp = buildURL(broken_tweet)
                found = lookUp(url) #try to find page each time a word is removed
                if found:
                    break;
        if not found: #removing articles did not help.
                    lastWord = broken_tweet[len(broken_tweet)-1]
                    if lastWord[len(lastWord)-1] == 's':
                        lastWord = broken_tweet[len(broken_tweet)-1]
                        broken_tweet[len(broken_tweet)-1] = lastWord[:len(lastWord)-1]
                        url, temp = buildURL(broken_tweet)
                        found = lookUp(url)
                        if found:
                            print('found by removing last word plural')
                    if not found:
                        found = lookUp_lastName(lastWord)
                        if found:
                            print('found by searching by last name')
                        else:
                            print('!!!!!!!!!!!!!!!!!!!!!!!could not find!!!!!!!!!!!!!!!!!!!!!!!')
else:
    if validUrl(inpho_json['url']):
        createResponse(inpho_json['url'], title)


