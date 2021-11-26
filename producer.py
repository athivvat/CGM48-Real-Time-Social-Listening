import tweepy
import settings
import re
from json import dumps
from dotenv import dotenv_values
from kafka import KafkaProducer
from bson import json_util
from requests import get

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

        # Get text message if it is a retweet
        try:
            is_retweeted = True if status.retweeted_status is not None else False
            text = status.retweeted_status.text
        except:
            is_retweeted = False
            text = status.text

        id_str = status.id_str
        created_at = status.created_at
        user_screen_name = status.user.screen_name
        user_created_at = status.user.created_at
        user_followers = status.user.followers_count
        user_location = status.user.location
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        retweets = status.retweet_count
        favorites = status.favorite_count
        replies = status.reply_count
        hashtags = [hashtag['text'] for hashtag in status.entities['hashtags']]

        # Clean
        text = clean_text(text)

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
            "hashtags": hashtags
        }

        print("Produce data: ", data, '\n')
        producer.send(topic_name, value=data)

    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False


def emojis() -> str:
    page = get(
        "https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt")
    lines = page.text.split("\n")

    blacklist = [  # blacklist of element who are not really emojis
        "number sign",
        "asterisk",
        "digit zero..digit nine",
        "copyright",
        "registered",
        "double exclamation mark",
        "exclamation question mark",
        "trade mark",
        "information"
    ]

    unicodes = []
    extendedEmoji = {}
    for line in lines:  # check all lines
        # ignores comment lines and blank lines
        if not line.startswith("#") and len(line) > 0:
            # check if the emoji isn't in the blacklist
            if line.split(')')[1].strip() not in blacklist:
                # recovery of the first column
                temp = f"{line.split(';')[0]}".strip()
                if ".." in temp:  # if it is a "list" of emojis, adding to a dict
                    extendedEmoji[temp.split("..")[0]] = temp.split("..")[1]
                else:
                    unicodes.append(temp)
    # removal of duplicates and especially of extra spaces
    unicodes = list(set(unicodes) - {""})

    def _uChar(string: str):  # choice between \u and \U in addition of the "0" to complete the code
        stringLen = len(string)
        if stringLen > 7:  # Can't be more than 7 anyways
            raise Exception(f"{string} is too long! ({stringLen})")
        u, totalLong = "U", 7  # Should be 7 characters long if it is a capital U
        if stringLen < 4:  # 4 characters long if smaller than 4
            u, totalLong = "u", 4  # Should be 4 characters long if it is a lowercase u
        resultat = ""
        while len(f"{resultat}{string}") <= totalLong:  # Adding the 0
            resultat += "0"
        # Return the right "U" with the right number of 0
        return f"\{u}{resultat}"

    for i in range(0, len(unicodes)):  # add unicode syntax to the list
        unicodes[i] = f"{_uChar(unicodes[i])}{unicodes[i]}"

    for mot in extendedEmoji.items():  # add unicode syntax to the dict
        extendedEmoji[mot[0]] = f"{_uChar(mot[1])}{mot[1]}"
        temp = f"{_uChar(mot[0])}{mot[0]}-{extendedEmoji[mot[0]]}"
        if temp not in unicodes:  # if not already in the list
            unicodes.append(temp)  # add the item to the list

    resultat = "["
    for code in unicodes:  # conversion of the list into a string with | to separate all the emojis
        resultat += f"{code}|"

    return f"{resultat[:-1]}]+"


def remove_link(string):
    '''
    Remove links from string
    '''
    return re.sub(r'http\S+', '', string)


def clean_text(string):
    string = re.sub(emojis(), '', string, flags=re.UNICODE)
    string = remove_link(string)
    return string


# Initialize instance of the subclass
stream = TwitterStream(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)

# Filter realtime Tweets by keyword
stream.filter(track=settings.TRACK_WORDS, languages=settings.LANGUAGES)
