import tweepy
import settings
import re
from json import dumps
from dotenv import dotenv_values
from kafka import KafkaProducer
# from transformers import pipeline

"""LOAD ENVIRONMENT VALUES"""
config = dotenv_values(".env")

"""API ACCESS KEYS"""

access_token = config['ACCESSS_TOKEN']
access_token_secret = config['ACCESS_TOKEN_SECRET']
consumer_key = config['CONSUMER_KEY']
consumer_secret = config['CONSUMER_SECRET']

bootstrap_servers = config['BOOTSTRAP_SERVER'] + ":" + config['BOOTSTRAP_PORT']

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda m: dumps(m).encode('utf-8'))

topic = 'twitter'

class TwitterStream(tweepy.Stream):

    def on_status(self, status):
        '''
        Extract info from tweets
        '''
        if status.retweeted:
            # Avoid retweeted info, and only original tweets will be received
            return True

        # Extract attributes from tweet
        id_str = status.id_str
        created_at = status.created_at
        text = clean_tweet(status.text)
        user_screen_name = status.user.screen_name
        user_created_at = status.user.created_at
        user_followers = status.user.followers_count
        user_location = status.user.location
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]

        retweetts = status.retweet_count
        favorites = status.favorite_count

        # TODO: Sentiment analysis
        # Default model DistilBERT, https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english
        # classifier = pipeline('sentiment-analysis')
        # result = classifier(text)
        
        # Produce message to Kafka
        data = {
            "id_str": id_str,
            "created_at": created_at,
            "text": text,
            "user_screen_name": user_screen_name,
            "user_created_at": user_created_at,
            "user_followers": user_followers,
            "user_location": user_location,
            "longitude": longitude,
            "latitude": latitude,
            "retweetts": retweetts,
            "favorites": favorites,
            "sentiment": {
                "bullish": 0,   # For those Tweets that denote a positive sentiment.
                "bearish": 0,   # For those Tweets that denote a negative sentiment.
                "neutral": 0    # For those Tweets that do not convey any discernible sentiment.
            }
        }
        producer.send(topic, value=data)


    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False

def clean_tweet(tweet):
    ''' 
    Use sumple regex statemnents to clean tweet text by removing links and special characters
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

# Initialize instance of the subclass
stream = TwitterStream(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
stream.filter(track=settings.TRACK_WORDS)