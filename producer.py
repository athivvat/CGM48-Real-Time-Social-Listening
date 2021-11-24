import tweepy
import settings
import re
from json import dumps
from dotenv import dotenv_values
from kafka import KafkaProducer
from bson import json_util

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
    value_serializer=lambda m: dumps(m, default=json_util.default).encode('utf-8'))

topic_name = config['KAFKA_TOPIC']

class TwitterStream(tweepy.Stream):

    def on_status(self, status):
        '''
        Extract info from tweets
        '''
        # Extract attributes from tweet
        id_str = status.id_str
        created_at = status.created_at
        text = status.text
        user_screen_name = status.user.screen_name
        user_created_at = status.user.created_at
        user_followers = status.user.followers_count
        user_location = status.user.location
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]

        is_retweeted = status.retweeted
        retweets = status.retweet_count
        favorites = status.favorite_count
        replies = status.reply_count
        
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
            "is_retweeted": is_retweeted,
            "retweets": retweets,
            "favorites": favorites,
            "replies": replies,
            "sentiment": {
                "positive": 0, 
                "negative": 0,
                "neutral": 0 
            }
        }
        # print(data)
        producer.send(topic_name, value=data)


    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False


def remove_emoji(string):
    '''
    Remove emojis from string
    '''
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def remove_link(string):
    '''
    Remove links from string
    '''
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', string, flags=re.MULTILINE)

# Initialize instance of the subclass
stream = TwitterStream(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
stream.filter(track=settings.TRACK_WORDS, languages=settings.LANGUAGES)