import urllib, json

def buildURL (broken_tweet):
    title = ""
    url = ""
    for word in broken_tweet:
        title = title + word + ' '
        url = url + word + '+'
        
    title = title[:-1]
    url = url[:-1]
    return url, title;

def lookUp (url):
    print('searching for: ' + url + ' instead')
    url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url
    inpho_json = json.load(urllib.urlopen(url))
    print(inpho_json)
    if inpho_json['responseDetails'] == None:
        print('page missing!')
    else:
        link = 'https://www.inphoproject.org' + inpho_json['url']

        response = 'InPhO - ' + title + ' - ' + link
        print(response)
    return;

full_tweet = "SEP: The Problem of Induction http://ift.tt/2nhKsKL #philosophy"

broken_tweet = full_tweet.split(" ")
del broken_tweet[0]
del broken_tweet[len(broken_tweet)-1]
del broken_tweet[len(broken_tweet)-1]

url, title = buildURL(broken_tweet);

#the above code segment will be used to parse @peoppenheimer's tweet.text

#this is the url used to extract the json data
url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url

#this next line opens the url and reads the json data
inpho_json = json.load(urllib.urlopen(url))

#new: ability to incrementally remove articles/extra words
#incomplete: dealing with search that returns 2+ articles for same search
if inpho_json['responseDetails'] == None:
    print('page missing!')

    for word in broken_tweet:
        if word.lower() == 'the' or word.lower() == 'of' or word.lower() == 'a' or \
           word.lower() == 'an' or word.lower() == 'for' or word.lower() == 'and' or \
           word.lower() == 'but' or word.lower() == 'or' or word.lower() == 'yet':
            print('removed article: ' + word)
            broken_tweet.remove(word)
            url, temp = buildURL(broken_tweet)
            lookUp(url)
else: 
    #this line finds the entry in the json for the url and concatenates 
    link = 'https://www.inphoproject.org' + inpho_json['url']

    response = 'InPhO - ' + title + ' - ' + link
    print(response)


