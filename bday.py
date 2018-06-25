#!/usr/bin/env python3
import tweepy, time, urllib.request, json, requests, smtplib
from urllib.request import urlopen
from requests import get
from datetime import date
from bs4 import BeautifulSoup
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

#function used to scrape photo from wikipedia
#returns link to photo or '' if none found
def getImg(soup):
    for tab in soup.find_all('table'):
        if tab.get('class')[0] == 'infobox':
            for image in tab.find_all('img'):
                link = 'https:' + image.get('src')
                return link
    return ''

#function used to decide whether to update_with_media or regular
#updates status either way with tweet constructed in main body
def bdayTweet(tweet, wiki):
    try:
        wikipage = urllib.request.urlopen('https://en.wikipedia.org/wiki/' + wiki)
        link = getImg(BeautifulSoup(wikipage, 'html.parser'))
        if len(link) > 0:
            open('img.jpg', 'wb').write(requests.get(link).content)
            api.update_with_media(filename = 'img.jpg', status = tweet)
        else:
            api.update_status(tweet)
    except Exception as e:
        sendEmail(wiki, str(e))
        
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
wiki_q = []
for thinker in thinkers_all:
    try:
        if 'url' in thinker:
            url = 'https://www.inphoproject.org' + thinker['url'] + '.json'

            curr_thinker = json.load(urlopen(url))

            if 'birth' in curr_thinker:
                if len(curr_thinker['birth']) != 0 and curr_thinker['birth'][0]['month'] != 0: #check for any birth date
                    if curr_thinker['birth'][0]['month'] == month and curr_thinker['birth'][0]['day'] == day: #check for matching birth date
                        if len(curr_thinker['related_thinkers']) != 0 or len(curr_thinker['related_ideas']) != 0: #check for enough info
                            if 'death' in curr_thinker and len(curr_thinker['death']) != 0: #check for death date
                                age = year - curr_thinker['birth'][0]['year']
                                tweet = curr_thinker['label'] + ' was born #OnThisDay ' + str(age) + ' years ago in ' + str(curr_thinker['birth'][0]['year']) + '.'
                                emoji = u'\U0001F389' #popper
                                
                                if 'sep_dir' in curr_thinker and len(curr_thinker['sep_dir']) != 0: #which link to include? is there an SEP article
                                    tweet = tweet + ' Read about them at the SEP at https://plato.stanford.edu/entries/' + curr_thinker['sep_dir']
                                else:
                                    tweet = tweet + ' \nLearn more at https://en.wikipedia.org/wiki/' + curr_thinker['wiki']
                                    
                                tweet = tweet + ' \nAlso, visit the InPhO entry at ' + emoji + ' https://www.inphoproject.org' + curr_thinker['url']
                                tweet_q.append(tweet)
                                wiki_q.append(curr_thinker['wiki'])
    except Exception as e:
        sendEmail(thinker['label'], str(e))
        
if len(tweet_q) > 0: #at least one bday
    bdayTweet(tweet_q[0], wiki_q[0])
    for i in range (1, len(tweet_q)):
        time.sleep(3600) #one hour
        bdayTweet(tweet_q[i], wiki_q[i])
