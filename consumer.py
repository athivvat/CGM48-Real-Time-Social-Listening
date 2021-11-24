import re
from kafka import KafkaConsumer, consumer
from pymongo import MongoClient
from dotenv import dotenv_values
import json

"""LOAD ENVIRONMENT VALUES"""
config = dotenv_values(".env")

topic_name = config['KAFKA_TOPIC']

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017')
    db = client.twitters
    print('Connected to MongoDB')
except:
    print('Could not connect to MongoDB')

consumer = KafkaConsumer(topic_name,
                         bootstrap_servers=[
                             'ec2-18-139-3-145.ap-southeast-1.compute.amazonaws.com:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         auto_commit_interval_ms=5000,
                         fetch_max_bytes=128,
                         max_poll_records=100,

                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

def sentiment_analysis(text):
    # Get sentiment score
    # sentiment_score = sentiment_analysis_client.sentiment_analysis(text)
    # return sentiment_score
    return 0

def engagement_score(text):
    # Get engagement score
    # engagement_score = engagement_score_client.engagement_score(text)
    # return engagement_score
    return 0

for message in consumer:
    record = json.loads(json.dumps(message.value))

    id_str = record['id_str']
    created_at = record['created_at']
    text = record['text']
    user_screen_name = record['user_screen_name']
    user_created_at = record['user_created_at']
    user_followers = record['user_followers']
    user_location = record['user_location']
    longitude = record['longitude']
    latitude = record['latitude']
    is_retweeted = record['is_retweeted']
    retweets = record['retweets']
    favorites = record['favorites']
    replies = record['replies']
    hashtags = record['hashtags']

    # Create dictionary and ingest data into mogoDB
    try:
        tweet_record = {
            "id_str": id_str,
            "created_at": created_at,
            "text": text,
            "user_screen_name": user_screen_name,
            "user_created_at": user_created_at,
            "user_followers": user_followers,
            "user_location": user_location,
            "is_retweeted": is_retweeted,
            "retweets": retweets,
            "favorites": favorites,
            "replies": replies,
            
            "hashtags": hashtags
        }
        print(tweet_record)
        record_id = db.tweets.insert_one(tweet_record)
        print('Inserted record with id:', record_id.inserted_id, '\n')
    except:
        print("Error: unable to create tweet dictionary")
