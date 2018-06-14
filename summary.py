#!/usr/bin/env python3
import tweepy, time, smtplib, urllib.request
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from keys import *

#function used to concatenate entries (revised or new)
#in readable string format
#returns a string of the entries passed in
def listEntries(entries):
    if len(entries) == 1:
        return entries[0]
    elif len(entries) == 2:
        return entries[0] + ' and ' + entries[1]
    else:
        result = entries[0] + ', '
        for entry in entries[1:-1]:
            result = result + entry + ', '
        result = result + 'and ' + entries[len(entries)-1]
        return result

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
        print('error sending mail')

#authentication for twitter bot access
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
myID = 974652683788455936

#authentication for gmail access
gmail_sender = 'inphotwitterbot@gmail.com' #create email for bot later
gmail_passwd = PASSWD
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_sender, gmail_passwd)

for x in range(1, 30): #remove loop when done testing

    try:
        yesterday = date.today() - timedelta(x)
        revised_auth = []
        revised = []
        added = []

        rss = urllib.request.urlopen('https://plato.stanford.edu/rss/sep.xml')
        soup = BeautifulSoup(rss, 'html.parser')
        response = ''
        for entry in soup.find_all('item'):
            pubdate = str(entry.pubdate)
            start = pubdate.find('<pubdate>') + 9
            pubdate = pubdate[start:-25]
            pubdate = datetime.strptime(pubdate, '%a, %d %b %Y').date()
            if pubdate == yesterday:
                desc = str(entry.description)
                start = desc.find('[')
                desc = desc[start+1:]

                start = desc.find(' by')
                end = desc.find(' on')
                byline = desc[start:end]
                
                if desc.split(' ')[0] == 'Revised':
                    revised.append(str(entry.title)[7:-8] )
                    revised_auth.append(str(entry.title)[7:-8] + byline)
                elif desc.split(' ')[0] == 'New':
                    added.append(str(entry.title)[7:-8] + byline)
                else:
                    sendEmail(date.strftime(yesterday, '%a %b %d'), 'Error reading RSS')
            elif pubdate < yesterday:
                #published before yesterday
                break
                
        tweet = ''
        if len(added) + len(revised) < 4:
            revised = revised_auth
            
        if len(added) > 0:
            if len(added) == 1:
                tweet = tweet + 'added ' + added[0] + ' as a new entry.'
            else: #>1
                tweet = tweet + 'added ' + listEntries(added) + ' as new entries.'
            if len(revised) > 0:
                tweet = tweet + ' Also, the SEP revised ' + listEntries(revised) + '.'
        elif len(revised) > 0:
            if len(revised) > 2:
                tweet = tweet + 'revised ' + str(len(revised)) + ' entries: ' + listEntries(revised) + '.'
            else:
                tweet = tweet + 'revised ' + listEntries(revised) + '.'

        if len(tweet) > 0:
            print(str(yesterday))
            tweet = 'Yesterday, ' + date.strftime(yesterday, '%b %d') + ', the SEP ' + tweet
            closing = ' To see more inpho and subscribe to live updates, follow both this account and @peoppenheimer.'
            if len(tweet) + len(closing) <= 280:
                tweet = tweet + closing
            print(tweet)
    except Exception as e:
        sendEmail(date.strftime(yesterday, '%a %b %d'), str(e))
