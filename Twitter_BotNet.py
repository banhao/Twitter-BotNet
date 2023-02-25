#!/usr/bin/env python3
#_*_coding: utf-8_*_
# Author: Hao Ban/banhao@gmail.com
# Version: 
# Issue Date: January 23, 2023
# Release Note:  


import json, hmac, hashlib, time, requests, base64, collections, statistics, os, string, random, subprocess, psutil, sys
import urllib.parse as urlparse
from urllib.parse import unquote, urlencode
from requests.auth import AuthBase
from datetime import datetime, timedelta, date
from cryptography.fernet import Fernet
from os import path
import dateutil.parser as dp
import xml.etree.ElementTree as ET
from xml.dom import minidom
from importlib import reload
from import_file import import_file
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException


def Twitter_authentication():
    oauth_tokens_list = {}
    # To set your enviornment variables in your terminal run the following line:
    # export 'CONSUMER_KEY'='<your_consumer_key>'
    # export 'CONSUMER_SECRET'='<your_consumer_secret>'
    consumer_key = variable.Twitter_API_key
    consumer_secret = variable.Twitter_API_key_secret
    #consumer_key = os.environ.get("CONSUMER_KEY")
    #consumer_secret = os.environ.get("CONSUMER_SECRET")
    for username, password in variable.Bot_List.items():
        driver = webdriver.Edge(executable_path=r'.\msedgedriver.exe')
        time.sleep(1)
        driver.get("https://twitter.com/login")
        time.sleep(3)
        driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input").send_keys(username)
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input").send_keys(password)
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div/span/span").click()
        time.sleep(1)
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print("There may have been an issue with the consumer_key or consumer_secret you entered.")
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)
        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        driver.get(authorization_url)
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[2]/div/form/fieldset/input[1]").click()
        time.sleep(1)
        verifier = driver.find_element(By.XPATH, "/html/body/div[2]/div/p/kbd/code").text
        print("PIN is %s" % verifier)
        driver.quit()
        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)
        oauth_tokens_list[username] = oauth_tokens
    return(oauth_tokens_list)


def Twitter(plot,MSG_BODY,tweets_count):
    index = random.randint(0, len(oauth_tokens_list)-1)
    print("Access Token index is:", index)
    tweets_count = tweets_count
    print(tweets_count)
    access_token = list(oauth_tokens_list.values())[index]['oauth_token']
    access_token_secret = list(oauth_tokens_list.values())[index]['oauth_token_secret']
    oauth = OAuth1(
        variable.Twitter_API_key,
        client_secret = variable.Twitter_API_key_secret,
        resource_owner_key = access_token,
        resource_owner_secret = access_token_secret,
    )
    MEDIA_SIZE = os.stat(plot).st_size
    request_data={ 'command': 'INIT', 'total_bytes': str(MEDIA_SIZE), 'media_type': 'image/png' }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, auth=oauth)
    if response.status_code != 202:
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    MEDIA_ID = str(response.json()['media_id'])
    request_data = { 'command': 'APPEND', 'media_id': MEDIA_ID, 'segment_index': '0' }
    file = open(plot, 'rb')
    files = { 'media':file.read() }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, files=files, auth=oauth)
    if response.status_code != 204 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    request_data = { 'command': 'FINALIZE', 'media_id': MEDIA_ID }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, auth=oauth)
    if response.status_code != 201 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    request_data = { "text": MSG_BODY, "media": {"media_ids": [MEDIA_ID]}}
    response = requests.post(url='https://api.twitter.com/2/tweets', json=request_data, auth=oauth)
    if response.status_code != 201 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    else:
        print("Post Successfully", response.json())
        if response.headers['x-rate-limit-remaining'] == '0':
            print("Exceeded Twitter API rate limits, start sleeping......")
            time.sleep(900)
#           time.sleep(int(float(response.headers['x-rate-limit-reset']) - float(time.time()))+60)
        else:
            print("Rate Limit Remaining:", response.headers['x-rate-limit-remaining'])
        try: 
            if str(response.json()['status']) == '429':
                print(response.headers)
                print(response.json())
                time.sleep(900)
        except Exception:
            pass


def Twitter_TimeLine(plot,MSG_BODY,tweet_id,tweets_count):
    index = random.randint(0, len(oauth_tokens_list)-1)
    print("Access Token index is:", index)
    tweets_count = tweets_count
    print(tweets_count)
    access_token = list(oauth_tokens_list.values())[index]['oauth_token']
    access_token_secret = list(oauth_tokens_list.values())[index]['oauth_token_secret']
    oauth = OAuth1(
        variable.Twitter_API_key,
        client_secret = variable.Twitter_API_key_secret,
        resource_owner_key = access_token,
        resource_owner_secret = access_token_secret,
    )
    MEDIA_SIZE = os.stat(plot).st_size
    request_data={ 'command': 'INIT', 'total_bytes': str(MEDIA_SIZE), 'media_type': 'image/png' }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, auth=oauth)
    if response.status_code != 202:
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    MEDIA_ID = str(response.json()['media_id'])
    request_data = { 'command': 'APPEND', 'media_id': MEDIA_ID, 'segment_index': '0' }
    file = open(plot, 'rb')
    files = { 'media':file.read() }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, files=files, auth=oauth)
    if response.status_code != 204 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    request_data = { 'command': 'FINALIZE', 'media_id': MEDIA_ID }
    response = requests.post(url="https://upload.twitter.com/1.1/media/upload.json", data=request_data, auth=oauth)
    if response.status_code != 201 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    request_data = { "text": MSG_BODY, "media": {"media_ids": [MEDIA_ID]}, "reply": {"in_reply_to_tweet_id": tweet_id}}
    response = requests.post(url='https://api.twitter.com/2/tweets', json=request_data, auth=oauth)
    if response.status_code != 201 :
        print("Request returned an error: {} {}".format(response.status_code, response.text))
        if response.status_code == 429 :
            time.sleep(900)
    else:
        print("Post Successfully", response.json())
        if response.headers['x-rate-limit-remaining'] == '0':
            print("Exceeded Twitter API rate limits, start sleeping......")
            time.sleep(900)
#           time.sleep(int(float(response.headers['x-rate-limit-reset']) - float(time.time()))+60)
        else:
            print("Rate Limit Remaining:", response.headers['x-rate-limit-remaining'])
        try: 
            if str(response.json()['status']) == '429':
                print(response.headers)
                print(response.json())
                time.sleep(900)
        except Exception:
            pass
 

def Twitter_user_followers(target_username):
    oauth = OAuth1(
        variable.Twitter_API_key,
        client_secret = variable.Twitter_API_key_secret,
        resource_owner_key = variable.Twitter_auth_key,
        resource_owner_secret = variable.Twitter_auth_secrett,
    )
    response = requests.get(url="https://api.twitter.com/2/users/by?usernames="+target_username+"&user.fields=public_metrics", auth=oauth)
    target_user_id = response.json()['data'][0]['id']
    followers_count = response.json()['data'][0]['public_metrics']['followers_count']
    following_count = response.json()['data'][0]['public_metrics']['following_count']
    if followers_count > 1000 :
        response = requests.get(url="https://api.twitter.com/2/users/"+target_user_id+"/followers?max_results=1000", auth=oauth)
        follower_list = response.json()['data']
        for i in range(int(followers_count/1000)):
            try:
                next_token = response.json()['meta']['next_token']
                response = requests.get(url="https://api.twitter.com/2/users/"+target_user_id+"/followers?max_results=1000&pagination_token="+next_token, auth=oauth)
                if response.headers['x-rate-limit-remaining'] == '0' :
                    print("Request returned an error: {} {}".format(response.status_code, response.text))
                    time.sleep(900)
                else:
                    for m in range(len(response.json()['data'])):
                        follower_list.append(response.json()['data'][m])
            except KeyError:
                print("The last page of the followers")
    elif followers_count == 0:
        print("No follower")
        follower_list = []
    else :
        response = requests.get(url="https://api.twitter.com/2/users/"+target_user_id+"/followers?max_results=1000", auth=oauth)
        follower_list = response.json()['data']
    return(follower_list)


def Twitter_Followers_TimeLine(target_follower_list):
    tweets_count = 0
    oauth = OAuth1(
        variable.Twitter_API_key,
        client_secret = variable.Twitter_API_key_secret,
        resource_owner_key = variable.Twitter_auth_key,
        resource_owner_secret = variable.Twitter_auth_secrett,
    )
    for i in range(len(target_follower_list)):
        follower_id = target_follower_list[i]['id']
        response = requests.get(url="https://api.twitter.com/2/users/"+follower_id+"/tweets", auth=oauth)
        if 'data' in response.json():
            print(response.json()['data'][0])
            tweet_id = response.json()['data'][0]['id']
            Twitter_TimeLine(plot,MSG,tweet_id,tweets_count)
            tweets_count += 1
        else:
            print(target_follower_list[i]['username'], "has no tweet.")
        time.sleep(3)
    print(tweets_count, "Tweets have been posted")


def Twitter_Followers(target_follower_list):
    tweets_count = 0
    oauth = OAuth1(
        variable.Twitter_API_key,
        client_secret = variable.Twitter_API_key_secret,
        resource_owner_key = variable.Twitter_auth_key,
        resource_owner_secret = variable.Twitter_auth_secrett,
    )
    if os.path.isfile('.\index.txt') and os.path.getsize('.\index.txt') > 0:
        with open("index.txt", "r") as file:
            tweets_count = json.load(file)
    for i in range(len(target_follower_list)):
        if tweets_count != 0:
            i = tweets_count
        follower_username = target_follower_list[i]['username']
        MSG_BODY = "@"+follower_username+" "+MSG
        Twitter(plot,MSG_BODY,tweets_count)
        tweets_count += 1
        with open('index.txt', 'w') as index:
            json.dump(tweets_count, index)
        time.sleep(3)
    print(tweets_count, "Tweets have been posted")


variable = import_file('./init.py')
target_username =  sys.argv[1]
MSG = sys.argv[2]
plot = sys.argv[3]
if os.path.isfile('.\Oauth_Token.json') and os.path.getsize('.\Oauth_Token.json') > 0:
    with open("Oauth_Token.json", "r") as file:
        oauth_tokens_list = json.load(file)
else:
    oauth_tokens_list = Twitter_authentication()
    with open('Oauth_Token.json', 'w') as Oauth_Token:
        json.dump(oauth_tokens_list, Oauth_Token)

if os.path.isfile('.\Target_Follower.json') and os.path.getsize('.\Target_Follower.json') > 0:
    with open("Target_Follower.json", "r") as file: 
        target_follower_list = json.load(file)
else:
    target_follower_list = Twitter_user_followers(target_username)
    with open('Target_Follower.json', 'w') as Target_Follower:
        json.dump(target_follower_list, Target_Follower)
Twitter_Followers(target_follower_list)
Twitter_Followers_TimeLine(target_follower_list)

