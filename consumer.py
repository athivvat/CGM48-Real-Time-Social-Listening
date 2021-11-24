from kafka import KafkaConsumer, consumer
from pymongo import MongoClient
import json

topic_name = 'TOPIC'

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017')
    db =client.twitter_nl
    print('Connected to MongoDB')
except:
    print('Could not connect to MongoDB')

consumer = KafkaConsumer(topic_name,
    bootstrap_servers=['ec2-18-139-3-145.ap-southeast-1.compute.amazonaws.com:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
    fetch_max_bytes=128,
    max_poll_records=100,

    value_deserializer=lambda m: json.loads(m.decode('utf-8')))

for message in consumer:
    record = json.loads(json.dumps(message.value))

    id_str = record['id_str']
    created_at = record['created_at']
    text = record['text']
    user_screen_name = record['user_screen_name']
    user_created_at = record['user_created_at']
    user_followers = record['user_followers_count']
    user_location = record['user_location']
    longitude = record['longitude']
    latitude = record['latitude']
    retweets = record['retweets']
    favorites = record['favorites']

    # Create dictionary and ingest data into mogoDB
    try:
        tweet_record = {
            "id_str": id_str,
            "created_at": created_at,
            "text": text,
            "user_screen_name": user_screen_name,
            "user_created_at": user_created_at,
            "user_followers_count": user_followers,
            "user_location": user_location,
            "longitude": longitude,
            "latitude": latitude,
            "retweets": retweets,
            "favorites": favorites,
            "sentiment": {
                "bullish": 0,   # For those Tweets that denote a positive sentiment.
                "bearish": 0,   # For those Tweets that denote a negative sentiment.
                "neutral": 0    # For those Tweets that do not convey any discernible sentiment.
            }
        }
        record_id = db.tweet_info.insert_one(tweet_record)
        print('Inserted record with id:', record_id)
    except:
        print("Error: unable to create tweet dictionary")