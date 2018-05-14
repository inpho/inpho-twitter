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

#function used to find the most recent reply to a dailysep tweet
#returns id of dailyseps tweet that was replied to
#returns -1 is not found in myTimeline given to function
def getLastReply(myTimeline, userID):
    for tweet in myTimeline:
        if tweet.in_reply_to_user_id == userID:
            return tweet.in_reply_to_status_id
    return -1

#function used to check if the query returns more than one result
#returns true if more than one result is found
#reutrns false otherwise
#error email sent if true
def isMultiple (inpho_json):
    resDat = inpho_json.get('responseData')
    res = resDat.get('results')
    if len(res) > 0: #there was >1 result
        sendEmail(res[0]['sep_dir'], 'Multiple results for this sep_dir.')
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
def createResponse (sep_url, url, title):
    entry = urllib.request.urlopen(sep_url)
    soup = BeautifulSoup(entry, 'html.parser')
    pub = soup.find(id ="pubinfo")
    start = str(pub).find('<em>')
    end = str(pub).find('</em>')
    if start == -1 or end == -1:
        sendEmail(title, 'Could not find pub info')
    pub = str(pub)[start+4:end]

    link = 'https://www.inphoproject.org' + url
    if url.split('/')[1] == 'thinker':
        emoji = u'\U0001F9E0' #brain emoji
    elif url.split('/')[1] == 'idea':
        emoji = u'\U0001F4A1' #lightbulb emoji
        
    response = 'This SEP entry was ' + pub + '.\n\nCheck \"' + title + '\" out on InPhO ' + 'emoji' + ' ' + link
    return response;

#function used to send an email in order to alert of errors found
#err is the specified error message based on the issue
#returns nothing, either sends email or doesn't.
def sendEmail(title, err):
##    TO = 'vmc12@pitt.edu'
##    SUBJECT = 'InPhO DailySEP Bot Error Alert'
##    TEXT = 'Error detected by bot for ' + title + ':\n' + err
##    BODY = '\r\n'.join(['To: %s' % TO,
##                    'From: %s' % gmail_sender,
##                    'Subject: %s' % SUBJECT,
##                    '', TEXT])
    try:
 #       server.sendmail(gmail_sender, [TO], BODY)
        print('email sent: ' + title + ': ' + err)
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

userID = 839300259838902272 #userID of @dailySEP
myID = 974652683788455936
myTimeline = api.user_timeline(user_id = myID, count = 5) #5 to match max response rate
last_reply_id = getLastReply(myTimeline, userID)

if last_reply_id != -1: #change to == after running once
    sendEmail('Initializing error', 'cannot find last dailySEP reply')
else:
    timeline = api.user_timeline(user_id = userID, count = 5, tweet_mode='extended') #change 5 based on frequency of running bot
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
            broken_tweet = status.full_text.split(" ")
            if broken_tweet[0] != 'RT': #tweet wasn't a retweet
                sep_url = broken_tweet[len(broken_tweet)-1]
                del broken_tweet[len(broken_tweet)-1]

                sep_url = requests.get(sep_url).url #get redirect URL

                sep_title = sep_url.split('/')
                sep_title = sep_title[len(sep_title)-2] #get sep_dir value to search by
                url = 'https://inphoproject.org/entity.json?sep=' + sep_title + '&redirect=True'
                
                inpho_json = json.load(urllib.request.urlopen(url))

                if 'url' not in inpho_json:
                    if not isMultiple(inpho_json):
                        sendEmail(status.full_text, 'Could not find page!')
                else:
                    title = inpho_json['label']
                    if validUrl(inpho_json['url']):
                        response = createResponse(sep_url, inpho_json['url'], title)
                        time.sleep(random.randint(60, 120))
                        api.update_status('@dailySEP ' + response, status.id)
                        print('tweet response: ' + response + ' to: ' + status.full_text)
