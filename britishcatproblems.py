#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twython import Twython, TwythonError
import time, sys, re, textwrap, glob, random, os
from PIL import Image, ImageDraw, ImageFont

app_key = ""
app_secret = ""
oauth_token = ""
oauth_token_secret = ""

twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

fonts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
font = ImageFont.truetype(os.path.join(fonts_path, "Impact.ttf"), 25)
rain = glob.glob("Rain/*")
tea = glob.glob("Tea/*")
british = glob.glob("British/*")
rain_words = ["rain", "rainy", "wet", "rains", "umbrella"]
tea_words = ["tea", "cuppa", "teacup", "teapot"]

while True:
    last_tweet = file("tweeted.txt", "r").readlines()[0]
    search_results = twitter.search(q = "#BritishCatProblems -RT",
                            count = 10,
                            since_id = int(last_tweet))
    try:
        for tweet in search_results["statuses"]:
            margin = offset = 15
            # Remove any URLs from Tweet
            no_url = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?������]))',
                            "",tweet["text"])
            no_hashtag = re.sub("#britishcatproblems","",no_url, flags = re.IGNORECASE)
            no_hashtag = re.sub(r"[^\x00-\x7F]+","", no_hashtag)
            # If Tweet has already been Tweeted, it's my own or Tweet is too long
            if tweet["user"]["screen_name"] == "SirBritCat" or len(no_url) > 110:
				with open("tweeted.txt", "w") as tweeted:
					tweeted.write(tweet["id_str"])
				if tweet["user"]["screen_name"] != "SirBritCat":
					twitter.update_status(status="@"+tweet["user"]["screen_name"]+" Sorry, your tweet is too long! Please make it less than 110 characters!")
            else:
                print no_url
                # Open random image
                if any(word in no_hashtag for word in rain_words):
                    open_image = Image.open(rain[random.randint(0,len(rain))-1])
                elif any(word in no_hashtag for word in tea_words):
                    open_image = Image.open(tea[random.randint(0,len(tea))-1])
                else:
                    open_image = Image.open(british[random.randint(0,len(british))-1])
                image = ImageDraw.Draw(open_image)
                # Text to generate on image
                image_text = no_hashtag+" - @"+tweet["user"]["screen_name"]
                # Get textbox size and convert to uppercase
                w, h = image.textsize(image_text.upper())
                # Add text outline
                for line in textwrap.wrap(image_text, width=50):
                    image.text((margin-2, offset-2),
                               line.upper(),
                               (0,0,0),
                               font = font)
                    image.text((margin+2, offset-2),
                               line.upper(),
                               (0,0,0),
                               font = font)
                    image.text((margin-2, offset+2),
                               line.upper(),
                               (0,0,0),
                               font = font)
                    image.text((margin+2, offset+2),
                               line.upper(),
                               (0,0,0),
                               font = font)
                    # Add white text
                    image.text((margin, offset),
                               line.upper(),
                               (255,255,255),
                               font = font)
                    # Move to next line
                    offset += font.getsize(line)[1]
                # Save image and open it
                open_image.save("tweetpic.jpg")
                tweetpic = open("tweetpic.jpg", "rb")
                image_ids = twitter.upload_media(media = tweetpic)
                # Update status with text and image
                twitter.update_status(status = "\"" + no_url + "\" - @" + tweet["user"]["screen_name"],
                                      media_ids = image_ids["media_id"])
                # Add Tweet ID to text file
                with open("tweeted.txt", "w") as tweeted:
                    tweeted.write(tweet["id_str"])
                # Sleep 1min - only after successful Tweet
        time.sleep(10)
    except TwythonError as e:
        print e
        time.sleep(10)
