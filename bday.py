#!/usr/bin/env python3
import tweepy, time, urllib.request, json, requests, smtplib
from urllib.request import urlopen
from requests import get
from datetime import date
from keys import *

#function used to send an email in order to alert of errors found
#err is the specified error message based on the issue
#returns nothing, either sends email or doesn't.
def sendEmail(name, errTime):
    TO = 'vmc12@pitt.edu'
    SUBJECT = 'InPhO Bot Error Alert'
    TEXT = 'Error detected by bot for birthday tweet of ' + name + ' on ' + errTime
    BODY = '\r\n'.join(['To: %s' % TO,
                    'From: %s' % gmail_sender,
                    'Subject: %s' % SUBJECT,
                    '', TEXT])
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent: ' + name + errTime)
    except:
        print('error sending mail: ' + name + errTime)
        
#authentication for twitter bot access
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

#authentication for gmail access
gmail_sender = 'inphotwitterbot@gmail.com'
gmail_passwd = PASSWD
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_sender, gmail_passwd)

today = str(date.today())
year = int(today[0:4])
month = int(today[5:7])
day = int(today[8:10])

thinkers = json.load(urlopen('https://www.inphoproject.org/thinker.json'))
thinkers_all = thinkers['responseData']['results']
tweet_q = []

for thinker in thinkers_all:
    try:
        if 'url' in thinker:
            url = 'https://www.inphoproject.org' + thinker['url'] + '.json'

            curr_thinker = json.load(urlopen(url))

            if 'birth' in curr_thinker:
                if len(curr_thinker['birth']) != 0 and curr_thinker['birth'][0]['month'] != 0:
                    if curr_thinker['birth'][0]['month'] == month and curr_thinker['birth'][0]['day'] == day: #bday is today
                        if len(curr_thinker['related_thinkers']) == 0 and len(curr_thinker['related_ideas']) == 0:
                            print('not enough for ' + curr_thinker['label'])
                        else:
                            age = year - curr_thinker['birth'][0]['year']
                            if 'death' in curr_thinker and len(curr_thinker['death']) != 0: #initial part of tweet depends on whether they are alive still
                                tweet = curr_thinker['label'] + ' was born #OnThisDay ' + str(age) + ' years ago in ' + str(curr_thinker['birth'][0]['year']) + '.'
                                emoji = u'\U0001F389' #popper
                            else:
                                tweet = 'Today is ' + curr_thinker['label'] + '\'s birthday. They are now ' + str(age) + ' years old. #OnThisDay'
                                emoji = u'\U0001F382' #bday cake
                                
                            if 'sep_dir' in curr_thinker and len(curr_thinker['sep_dir']) != 0: #which link to include? is there an SEP article
                                tweet = tweet + ' Read about them at the SEP at https://plato.stanford.edu/entries/' + curr_thinker['sep_dir']
                            else:
                                tweet = tweet + ' \nLearn more at https://en.wikipedia.org/wiki/' + curr_thinker['wiki']
                                
                            tweet = tweet + ' \nAlso, visit the InPhO entry at ' + emoji + ' https://www.inphoproject.org' + curr_thinker['url']
                            tweet_q.append(tweet)
    except Exception as e:
        sendEmail(thinker['label'], str(e))
if len(tweet_q) > 0: #at least one bday
    api.update_status(tweet_q[0])
    for i in range (1, len(tweet_q)):
        time.sleep(3600) #one hour
        api.update_status(tweet_q[i])
