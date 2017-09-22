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
           	print(tweet['text'])

#             # Respond to the tweet with one of the response lines

#             # check to see if Analyze: is present
#             if "Analyze:" in tweet["text"]:        
#                 tweet_id = tweet["id"]
#                 words = tweet["text"].lower().split("analyze")
#                 sender_account = tweet['user']['screen_name']
#                 target_account = tweet['entities']['user_mentions'][len(tweet['entities']['user_mentions'])-1]['screen_name']     
#                 returnResponse = "New Tweet Analysis: %s (Thx @%s!)" % (target_account, sender_account)

#                 runAnalysis(target_account, maxTweets)

# #                 Create a status update
#                 api.update_with_media(filename="@%s.png" % target_account,
#                                       status=returnResponse)

    return (last_id)


# Main

maxTweets = 200
# while(True):
for x in range(2):
    last_since_id = mentionedTweets(searchstring, last_since_id, maxTweets)
    
    # time.sleep(60)

print ('Complete')