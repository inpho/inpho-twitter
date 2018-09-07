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
def sendEmail(errTime, desc):
    TO = 'vmc12@pitt.edu'
    SUBJECT = 'InPhO Bot Error Alert'
    TEXT = 'Error detected by bot for summary tweet for ' + errTime + ': ' + desc
    BODY = '\r\n'.join(['To: %s' % TO,
                    'From: %s' % gmail_sender,
                    'Subject: %s' % SUBJECT,
                    '', TEXT])
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent: ' + errTime + desc)
    except:
        print('error sending mail')

#function used to parse tweets to find corresponding response
#returns string with link to status, or empty string if error
def getLink(byline, myID):
    title = byline[1:byline.find('\" by')]
    myTimeline = api.user_timeline(user_id = myID, count = 30)
    for status in myTimeline:
        if status.in_reply_to_user_id == 12450802: #peoppenheimer ID
            curr = status.text[22:]
            if title == curr[:curr.find('\" ')]:
                return 'https://twitter.com/peoppenheimer/status/' + status.id_str
            
    sendEmail(byline, 'Could not find corresponding status link')
    return ''
    
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

try:
    yesterday = date.today() - timedelta(1)
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
                revised.append('\"' + str(entry.title)[7:-8] + '\"')
                revised_auth.append('\"' + str(entry.title)[7:-8] + '\"' + byline)
            elif desc.split(' ')[0] == 'New':
                added.append('\"' + str(entry.title)[7:-8] + '\"' + byline)
            else:
                sendEmail(date.strftime(yesterday, '%a %b %d'), 'Error reading RSS')
        elif pubdate < yesterday:
            #published before yesterday
            break
            
    tweet = ''
    if len(added) + len(revised) < 4:
        revised = revised_auth

    star = u'\U00002728' + ' '
    memo = u'\U0001F4DD' + ' '

    updateLen = len(added) + len(revised)
    if updateLen > 0: #check for any updates
        #always have this beginning
        tweet = 'Yesterday, ' + date.strftime(yesterday, '%b %d') + ', the SEP '
        closing = ' To see more inpho and subscribe to live updates, follow both this account and @peoppenheimer.'
        shortclose = ' For more, follow us and @peoppenheimer.'
        #third option: no close.

        #format added entries
        if len(added) > 0:
            if len(added) == 1:
                tweet = tweet + 'added ' + star + added[0] + ' as a new entry.'
            else: #>1
                tweet = tweet + 'added ' + star + listEntries(added) + ' as new entries.'
            if len(revised) > 0:
                tweet = tweet + ' Also, the SEP '
                
        #format revised entries
        if len(revised) > 0:
            if len(revised) > 2:
                tweet = tweet + 'published a revised ' + memo + 'version of ' + str(len(revised)) + ' entries'
                #in the case of many revisions, only include as many as possible, truncate the rest. max 280 char
                if len(tweet) + len(listEntries(revised)) > 280:
                    tweet = tweet + ', including: '
                    while len(tweet) + len(listEntries(revised)) > 280:
                        revised = revised[:-1]
                else:
                    tweet = tweet + ': '
                tweet = tweet + listEntries(revised)
                if len(tweet) < 280:
                    tweet = tweet + '.'
            else:
                tweet = tweet + 'published a revised  ' + memo + 'version of ' + listEntries(revised) + '.'

        #now, check for length to determine what closing to use
        if len(tweet) + len(closing) <= 280:
            tweet = tweet + closing
        elif len(tweet) + len(shortclose) <= 280:
            tweet = tweet + shortclose
        #else, add no closing.

        #if only one update, include a link to the tweet    
        if updateLen == 1:
            if len(added) == 1:
                tweet = tweet + getLink(added[0], myID)
            else:
                tweet = tweet + getLink(revised[0], myID)
        api.update_status(tweet)
        
except Exception as e:
    sendEmail(date.strftime(yesterday, '%a %b %d '), str(e))
