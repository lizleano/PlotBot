
# coding: utf-8

# In[1]:

# Dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import tweepy
import time
import seaborn as sns

# Initialize Sentiment Analyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Twitter API Keys from file
# csvpath = "Keys.py"

key_pd = pd.read_csv("KeysTW.py")
consumer_key = key_pd[key_pd['Name']== 'TW_consumer_key']['key'].max().strip()
consumer_secret = key_pd[key_pd['Name']== 'TW_consumer_secret']['key'].max().strip()
access_token = key_pd[key_pd['Name']== 'TW_access_token']['key'].max().strip()
access_token_secret = key_pd[key_pd['Name']== 'TW_access_token_secret']['key'].max().strip()



# Target Account
searchstring = "@ldleanoBot"


# variables to hold last tweet id
last_since_id = 0

# Setup Tweepy API Authentication
def authorize():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    return api

def createChart(sentiments_pd, target_user):
    # Create plot
    plt.plot(sentiments_pd["Tweets Ago"],
             sentiments_pd["Compound"], marker="o", linewidth=0.5,
             alpha=0.8, label=target_user)

    # # Incorporate the other graph properties
    plt.title("Sentiment Analysis of Tweets (%s)" % (time.strftime("%x")))
    plt.ylabel("Tweet Polarity")
    plt.xlabel("Tweets Ago")
    
    plt.legend(title="Tweets", bbox_to_anchor=(1.30,1))

    fig = plt.gcf()
    plt.show()
    plt.draw()
    
    figurename = "%s.png" % target_user
    fig.savefig(figurename, bbox_inches='tight')


# function to plot analysis
def runAnalysis(target, numberOfTweets):
    tweetRange = int(numberOfTweets/100)
    
    # Setup Tweepy API Authentication
    api = authorize()
        
    # set arrays for sentiments
    sentiments_array=[]

    
    target_since_id = 0
    counter = 0
 
    for x in range(tweetRange):
        try:
            public_tweets = api.user_timeline("@%s" % (target), count=100, page=x)
        except:
            print ("Error getting tweets page=%s", x)
            
        # more data to process
        if (len(public_tweets) > 0):
            # force break
            if (len(public_tweets) < 100):
                print('force break')
                counter = numberOfTweets

            target_since_id = public_tweets[0]["id"]
            for tweet in public_tweets:
                tweettext = tweet["text"]

                target_string = tweettext
                # Run Vader Analysis on each tweet
                compound = analyzer.polarity_scores(tweet["text"])["compound"]
                pos = analyzer.polarity_scores(tweet["text"])["pos"]
                neu = analyzer.polarity_scores(tweet["text"])["neu"]
                neg = analyzer.polarity_scores(tweet["text"])["neg"]

                tweetsago = -counter

                # Add sentiments for each tweet into an array                
                sentiments_array.append({"Date": tweet["created_at"],
                                   "Tweets Ago": tweetsago,
                                   "Compound": compound,
                                   "Positive": pos,
                                   "Negative": neu,
                                   "Neutral": neg}) 

                # Add to counter 
                counter += 1

    if (len(sentiments_array) > 0):
        # Convert sentiments to DataFrame
        sentiments_pd = pd.DataFrame.from_dict(sentiments_array)
        
        createChart(sentiments_pd, "@%s" % target)    

        # clear array
        del sentiments_array[:]

# function to get all mentioned tweets
def mentionedTweets(mentionString, tweet_since_id, maxTweets):
    last_id = tweet_since_id
    api = authorize()    

    if (tweet_since_id > 0):
        public_tweets = api.search(mentionString, count=100, result_type="recent", since_id=last_id)
    else:
        public_tweets = api.search(mentionString, count=100, result_type="recent")
   
    #  get last tweet id
    if (len(public_tweets['statuses']) > 0):
        last_id = public_tweets['statuses'][0]["id"]

        # Loop through all tweets for mentions and pickup the name of target account to analyze 
        for tweet in public_tweets['statuses']:
            # check to see if Analyze: is present
            if "Analyze:" in tweet["text"]:        
                tweet_id = tweet["id"]
                words = tweet["text"].lower().split("analyze")
                sender_account = tweet['user']['screen_name']
                target_account = tweet['entities']['user_mentions'][len(tweet['entities']['user_mentions'])-1]['screen_name']     
                returnResponse = "New Tweet Analysis: %s (Thx @%s!)" % (target_account, sender_account)

                runAnalysis(target_account, maxTweets)

#                 Create a status update
                api.update_with_media(filename="@%s.png" % target_account,
                                      status=returnResponse)

                api.update_with_media(filename="@%s.png" % target_account,
                                      status=returnResponse,
                                      in_repy_to_status_id=tweet_id)

    return (last_id)


# Main

maxTweets = 500
while(True):
    last_since_id = mentionedTweets(searchstring, last_since_id, maxTweets)
    
    time.sleep(60)