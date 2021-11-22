import tweepy
from json import dumps
from dotenv import dotenv_values
from kafka import KafkaProducer

"""LOAD ENVIRONMENT VALUES"""
config = dotenv_values(".env")

"""API ACCESS KEYS"""

access_token = config['ACCESSS_TOKEN']
access_token_secret = config['ACCESSS_TOKEN_SECRET']
consumer_key = config['CONSUMER_KEY']
consumer_secret = config['CONSUMER_SECRET']


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda m: dumps(m).encode('utf-8'))

topic = 'twitter'

class TwitterAuth():
    """SET UP TWITTER AUTHENTICATION"""
    def authenticateTwitterApp(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth
    
class TwitterStreamer():
    """STREAM TWITTER DATA"""
    def __init__(self):
        self.twitterAuth = TwitterAuth()

    def stream_tweets(self, auth):
        listener = TwitterListener()
        stream = tweepy.Stream(auth, listener)
        stream.filter(track=['#'])

class TwitterListener(tweepy.StreamListener):
    def on_data(self, data):
        producer.send(topic, value=data)
        return True

if __name__ == "__main__":
    TS = TwitterStreamer()
    TS.stream_tweets()