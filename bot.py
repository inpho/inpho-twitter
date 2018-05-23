#!/usr/bin/env python3
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import tweepy, time, urllib.request, urllib.parse, urllib.error, json, requests, smtplib, random
from urllib.parse import quote
from requests import get
from bs4 import BeautifulSoup
from keys import *

#function used to find the most recent reply to a peoppenheimer tweet
#returns id of peoppenheimers tweet that was replied to
#returns -1 is not found in myTimeline given to function
def getLastReply(myID, myCount, user):
    getCount = 5
    start = 0
    while getCount < myCount:
        myTimeline = api.user_timeline(user_id = myID, count = getCount)
        for i in range(start, len(myTimeline)):
            tweet = myTimeline[i]
            rt_link = tweet.entities['urls'][0]['expanded_url'].split('/')
            tweet_user = rt_link[3]
            if tweet_user == user:
                return rt_link[len(rt_link)-1] #status id of last responded to tweet
        start = getCount
        getCount = getCount * 2
    return -1

#function used to add ' ' in between words from the tweet
#returns title: the formal title of the article
def buildTitle(broken_tweet):
    title = ""
    for word in broken_tweet:
        title = title + word + ' '
        
    title = title[:-1]
    return title;

#function used to check if the query returns more than one result
#returns true if more than one result is found
#reutrns false otherwise
#error email sent if true
def isMultiple (inpho_json):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result
        sendEmail(title, 'Multiple results for same sep_dir.')
        return True; #notify of error
    return False;

#function to check url is valid for responding with
    #currently checks if article is from the "school of thought" ontology
    #or if the link returns an error
#returns false if it is,
#returns true otherwise
#error email sent for 500 error
def validUrl (url):
    try:
        check = urllib.request.urlopen('https://www.inphoproject.org' + url)
    except urllib.error.HTTPError as e:
        sendEmail(title, '500 error on site.')
        return False;
    if url.split('/')[1] == 'school_of_thought':
        sendEmail(title, 'found in school of thought.')
        return False;
    elif url.split('/')[1] == 'work':
        sendEmail(title, 'found in work.')
        return False;
    elif url.split('/')[1] == 'journal':
        sendEmail(title, 'found in journal.')
        return False;
    return True;

#function that assembles the reply tweet from the url and title
#retrieves update message from SEP RSS
#returns response: the message to be tweeted back
#error email sent if no RSS info
def createResponse (url, title):
    rss = urllib.request.urlopen('https://plato.stanford.edu/rss/sep.xml')
    soup = BeautifulSoup(rss, 'html.parser')
    response = ''
    for entry in soup.find_all('item'):
        if str(entry.title) == '<title>' + title + '</title>':
            start = str(entry.description).find('[')
            end = str(entry.description).find(']')
            if start == -1 or end == -1:
                sendEmail(title, 'RSS format error')
            else:
                response = shortenRSS(str(entry.description)[start+1:end])
            break;
    if response == '':
        sendEmail(title, 'Could not find matching rss description.')
        return response;
    link = 'https://www.inphoproject.org' + url
    if url.split('/')[1] == 'thinker':
        emoji = u'\U0001F9E0' #brain emoji
    elif url.split('/')[1] == 'idea':
        emoji = u'\U0001F4A1' #lightbulb emoji
    elif url.split('/')[1] == 'taxonomy':
        emoji = u'\U0001F5C2' #files emoji
    else:
        emoji = u'\U0001F4AD' #default thought bubble emoji
    response = 'SEP\'s \"' + title + '\" is a ' + response + '\n\nCheck it out on InPhO ' + emoji + ' ' + link
    return response;

#function that reads in the RSS description and removes side files
#returns the same RSS description without files like *.html, etc.
def shortenRSS(description):
    start = description.find(': ')
    if start == -1: #no files found
        return description
    else:
        start = start + 2
        changed_files = description[start:].split(', ')
        description = description[:start]
        foundSupp = False
        for file in changed_files:
            if file.find('.') == -1:
                description = description + file + ', '
            else:
                foundSupp = True
        if foundSupp:
            description = description + 'supplemental files'
            return description
        else:
            return description[:-2]

#function used to send an email in order to alert of errors found
#err is the specified error message based on the issue
#returns nothing, either sends email or doesn't.
def sendEmail(title, err):
##    TO = 'vmc12@pitt.edu'
##    SUBJECT = 'InPhO Bot Error Alert'
##    TEXT = 'Error detected by bot for entry ' + title + ':\n' + err
##    BODY = '\r\n'.join(['To: %s' % TO,
##                    'From: %s' % gmail_sender,
##                    'Subject: %s' % SUBJECT,
##                    '', TEXT])
    try:
 #       server.sendmail(gmail_sender, [TO], BODY)
        print('email sent: ' + title + err)
    except:
        print('error sending mail')

#authentication for twitter bot access
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

#authentication for gmail access
##gmail_sender = 'vanessa.colihan@gmail.com' #create email for bot later
##gmail_passwd = PASSWD
##server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
##server.ehlo()
##server.login(gmail_sender, gmail_passwd)

userID = 12450802 #userID of peoppenheimer
user = 'peoppenheimer'
myID = 974652683788455936
myCount = api.get_user(myID).statuses_count
last_reply_id = getLastReply(myID, myCount, user)

if last_reply_id == -1:
    sendEmail('Initializing error: ', 'cannot find last peoppenheimer reply')
else:
    timeline = api.user_timeline(user_id = userID, count = 5) #change 5 based on frequency of running bot
    #note count must be <=15 to be able to read info from rss feed (only shows 15 latest)
    last_index = len(timeline)
    for x in range(0, len(timeline)):    
        if timeline[x].id == last_reply_id:
            last_index = x
    timeline = timeline[:last_index] #truncates tweets bot has already replied to
    #timeline returns count number of tweets from specified user, in order of most recent to least recent

    #reverse the order of timeline so that they are replied to in the opposite order
    for i in range(len(timeline)-1, -1, -1):

        status = timeline[i]

        if status.id == last_reply_id:
            break;
        else:
            broken_tweet = status.text.split(" ")
            if broken_tweet[0] == 'SEP:': #tweet must be a SEP tweet
                del broken_tweet[0]
                del broken_tweet[len(broken_tweet)-1]
                sep_url = broken_tweet[len(broken_tweet)-1]
                del broken_tweet[len(broken_tweet)-1]

                title = buildTitle(broken_tweet);
                
                sep_url = requests.get(sep_url).url #get redirect URL
                sep_url = sep_url.split('/')
                sep_title = sep_url[len(sep_url)-2] #get sep_dir value to search by
                url = 'https://inphoproject.org/entity.json?sep=' + sep_title + '&redirect=True'
                
                inpho_json = json.load(urllib.request.urlopen(url))
                
                if 'url' not in inpho_json:
                    if not isMultiple(inpho_json):
                        sendEmail(title, 'Could not find page!')
                else:
                    if validUrl(inpho_json['url']):
                        response = createResponse(inpho_json['url'], title)
                        if response != '':
                            time.sleep(random.randint(60, 120))
#                           api.update_status('@peoppenheimer ' + response, status.id)
                            api.update_status(response + ' https://twitter.com/peoppenheimer/status/' + status.id_str)

