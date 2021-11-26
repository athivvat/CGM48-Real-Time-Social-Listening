from kafka import KafkaConsumer, consumer
from pymongo import MongoClient
from dotenv import dotenv_values
from nltk.classify import apply_features
from nltk import FreqDist
import numpy as np
import re
import json
import pickle
import deepcut

"""LOAD ENVIRONMENT VALUES"""
config = dotenv_values(".env")

topic_name = config['KAFKA_TOPIC']

# Connect to MongoDB
try:
    client = MongoClient(config['MONGODB_URI'])
    db = client.twitter
    print('Connected to MongoDB')
except:
    print('Could not connect to MongoDB')
    exit()

consumer = KafkaConsumer(topic_name,
                         bootstrap_servers=[
                             'ec2-18-139-3-145.ap-southeast-1.compute.amazonaws.com:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         auto_commit_interval_ms=5000,
                         fetch_max_bytes=128,
                         max_poll_records=100,

                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))


'''
Sentiment Analysis
'''
data_pos = [(line.strip(), 'pos') for line in open("sentiment/neg.txt", 'r', encoding="utf8")]
data_neg = [(line.strip(), 'neg') for line in open("sentiment/pos.txt", 'r', encoding="utf8")]

def split_words (sentence):
    return deepcut.tokenize(''.join(sentence.lower().split()))
    
sentences = [(split_words(sentence), sentiment) for (sentence, sentiment) in data_pos + data_neg]
def get_words_in_tweets(tweets):
        all_words = []
        for (words, sentiment) in tweets:
          all_words.extend(words)
        return all_words

def get_word_features(wordlist):
    wordlist = FreqDist(wordlist)
    word_features = [word[0] for word in wordlist.most_common()]
    return word_features

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

# Load the model
sentiment_model = pickle.load(open('sentiment/my_classifier.pickle', 'rb'))

word_features = None

word_features = get_word_features(get_words_in_tweets(sentences))

# Consume tweets from Kafka
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

    # Sentiment
    sentiment_score = sentiment_model.classify(extract_features(text.split()))
    sentement = 1 if sentiment_score == 'pos' else 0
    print(sentement)

    '''
    Save to MongoDB
    '''
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
            "longitude": longitude,
            "latitude": latitude,
            "is_retweeted": is_retweeted,
            "retweets": retweets,
            "favorites": favorites,
            "replies": replies,
            "hashtags": hashtags,
            "sentiment": sentement
        }

        print(tweet_record)
        
        result = db.tweets.update_one({'id_str': tweet_record['id_str']}, {'$set': tweet_record}, upsert=True)
        if result.upserted_id is None:
            print("Upserted result: Tweet already exists", '\n')
        else:
            print('Upserted result:', result.upserted_id, '\n')
    except Exception as error:
        print('Error:', error)
