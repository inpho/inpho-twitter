import urllib, json

full_tweet = "SEP: Probabilistic Causation https://t.co/Y8MwSQ1kzT #philosophy"

broken_tweet = full_tweet.split(" ")
del broken_tweet[0]
del broken_tweet[len(broken_tweet)-1]
del broken_tweet[len(broken_tweet)-1]

title = ""
url = ""
for i in range (0, len(broken_tweet)-1):
    title = title + broken_tweet[i] + ' '
    url = url + broken_tweet[i] + '+'
    
title = title + broken_tweet[len(broken_tweet)-1]
url = url + broken_tweet[len(broken_tweet)-1]

#the above code segment will be used to parse @peoppenheimer's tweet.text

#this is the url used to extract the json data
url = 'https://www.inphoproject.org/entity.json?redirect=true&q=' + url

#this next line opens the url and reads the json data
inpho_json = json.load(urllib.urlopen(url))
#this line finds the entry in the json for the url and concatenates 
link = 'https://www.inphoproject.org' + inpho_json['url']

response = 'InPhO - ' + title + ' - ' + link
print(response)
