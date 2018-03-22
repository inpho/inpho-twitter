import urllib, json

full_tweet = "SEP: The Problem of Induction http://ift.tt/2nhKsKL #philosophy"

broken_tweet = full_tweet.split(" ")
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

#the above code segment will be used to parse @peoppenheimer's tweet.text

#this is the url used to extract the json data
url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url

#this next line opens the url and reads the json data
inpho_json = json.load(urllib.urlopen(url))

#new: check to see if page exists.
#incomplete: removing articles from search. current test case only works without 'the', but requires 'of'
if inpho_json['responseDetails'] == None:
    print('page missing!')
    url = ""
    for word in broken_tweet:
        if word.lower() == 'the' or word.lower() == 'of' or word.lower() == 'a' or \
           word.lower() == 'an' or word.lower() == 'for' or word.lower() == 'and' or \
           word.lower() == 'but' or word.lower() == 'or' or word.lower() == 'yet':
            print('removed article: ' + word)
        else:
            url = url + word + '+'
    url = url[:-1]
    print('searching for: ' + url + ' instead')
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.urlopen(url))
    print(inpho_json)
    link = 'https://www.inphoproject.org' + inpho_json['url']

    response = 'InPhO - ' + title + ' - ' + link
    print(response)
else: 
    #this line finds the entry in the json for the url and concatenates 
    link = 'https://www.inphoproject.org' + inpho_json['url']

    response = 'InPhO - ' + title + ' - ' + link
    print(response)
