from django.http.response import HttpResponse
from django.shortcuts import render
import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np
import re 
import matplotlib.pyplot as plt
import itertools
import collections
plt.style.use('fivethirtyeight')

log = pd.read_csv('Login.csv')

consumerKey = log['API_key'][0]
consumer_secret_key = log['API_key'][1]
accessToken = log['API_key'][2]
accessTokenSecret = log['API_key'][3]

authenticate = tweepy.OAuthHandler(consumerKey,consumer_secret_key)

authenticate.set_access_token(accessToken,accessTokenSecret)

api = tweepy.API(authenticate,wait_on_rate_limit= True)


print(consumerKey)

# Create your views here.
def index(request):
    context = {'a':1}
    return render(request,'index.html',context)

def cleanText(text):
    text = re.sub(r'@[A-Za-z0-9]+','',text)
    text = re.sub(r'#','',text)
    text = re.sub(r'RT[\s]+','',text)
    text = re.sub(r'https?:\/\/\S+','',text)
    regex = re.compile(r'[\n\r\t]')
    text = regex.sub(" ", text)
    text =re.sub("(?m)^\s+", "", text)
    return text

def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text):
    return TextBlob(text).sentiment.polarity

def getAnalysis(score):
    if score < 0:
        return 'Negative'
    if score == 0:
        return 'Neutral'
    if score > 0:
        return 'Positive'

def sentiment(request):
    search_word = ''
    date = 0
    number = 0
    posts = []
    if 'input_text' in request.GET:
        search_word = request.GET['input_text']
    
    if 'date' in request.GET:
        date = request.GET['date']
    
    if 'num' in request.GET:
        number = request.GET['num']
    while True:
        try:
            tweets = tweepy.Cursor(api.search,search_word,lang = 'en',since = date).items(100)
            for tweet in tweets:
                posts.append(tweet.text)
            df = pd.DataFrame(posts,columns = ['Tweets'])
            print(df['Tweets'][0])
            df['Tweets'] = df['Tweets'].apply(cleanText)
            df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
            df['Polarity'] = df['Tweets'].apply(getPolarity)
            df['Analysis'] = df['Polarity'].apply(getAnalysis)
            pos_count = 0
            neu_count = 0
            neg_count = 0
            for i in df['Analysis']:
                if i == 'Positive':
                    pos_count = pos_count + 1
                elif i == 'Neutral':
                    neu_count = neu_count + 1
                else:
                    neg_count = neg_count + 1
            context = {'search_word':search_word,'date_since': date,'Positive':pos_count,'Negative':neg_count,'Neutral':neu_count,'Sample_Tweet':df['Tweets'][0]}
            return render(request,'index.html',context)
    
        except:
            continue
        