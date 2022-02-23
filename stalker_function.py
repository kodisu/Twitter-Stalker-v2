
import os
import requests
import json
from datetime import datetime
import pytz 
from time import sleep
import discord
import traceback
import random
###### make sure db supports emojis https://stackoverflow.com/questions/39463134/how-to-store-emoji-character-in-mysql-database

### FUNCTION TO CONVERT STRING TO LIST
# list1=list(string1.split())


import os
from discord import Webhook, RequestsWebhookAdapter, File

os.environ["DISCORD_WEBHOOK"] = "your webhook"
os.environ["TWITTER_BEARER"] = "Bearer your bearer"
webhook_url = os.environ['DISCORD_WEBHOOK']

webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())


###Accounts to Stalk###
# these are the twitter accounts whos "following" list we are stalking
# supports 10 accounts per Twitter API instance
accounts = [
  "elonmusk","mcuban",
  ]


#FUNCTIONS FOR PICKLE
# following.pkl is for user_id, current_following key value pairs
import pickle
def pickle_following_import(id, current_following):
    f = open("following.pkl", "rb")
    data = pickle.load(f)
    f = open("following.pkl", "wb")
    #append arg
    data[id] = current_following
    pickle.dump(data, f)
    f.close()

def pickle_following_export(): #only use for printing
    f = open("following.pkl", "rb")
    data = pickle.load(f)
    return data

def pickle_following_reset():
  f = open("following.pkl", "wb")
  data = {}
  data[122]={1234:[{"id":123},{"username":"abc"}]}
  pickle.dump(data,f)
  f.close()


import mysql.connector
mydb = mysql.connector.connect(
  host="",
  user="",
  password="",
  database=""
)
mycursor = mydb.cursor()

def insert(sql, val):
  mycursor.execute(sql, val)
  mydb.commit()
  print("new Insert:", mycursor.lastrowid)

def select(sql, val):
  myresult = None
  # try: 
  mycursor.execute(sql, val)
  myresult = mycursor.fetchone()
  # except mysql.connector.errors.ProgrammingError:
  #   print("error in sql select")
  return myresult


#FUNCTIONS FOR STALKER#
def get_id(username):
  # sleep(2)
  url = "https://api.twitter.com/2/users/by/username/" + username
  bearer =  os.environ['TWITTER_BEARER']
  payload={}
  headers = {
    'Authorization': bearer,
    'Cookie': 'guest_id=v1%111; personalization_id="111=="'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  parsed = json.loads(response.text)
  # print(parsed)
  # print(parsed["data"]["id"])
  return(parsed["data"]["id"])

def get_followers_count(username):
  #try to store projects id and username in sql or pickle
  # https://api.twitter.com/2/users/[ID]?user.fields=public_metrics

  url = "https://api.twitter.com/2/users/"+ get_id(username) +"?user.fields=public_metrics"
  bearer =  os.environ['TWITTER_BEARER']
  payload={}
  headers = {
    'Authorization': bearer,
    'Cookie': 'guest_id=v1%111; personalization_id="111=="'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  parsed = json.loads(response.text)
  return(parsed["data"]["public_metrics"]["followers_count"])

def get_followers(username):
  url = "https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name="+username+"&count=5000"
  # MANUALLY ADD bearer for twitter v1.1 api
  payload={}
  headers = {
    'Authorization': 'Bearer your twitter api v1.1'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  parsed = json.loads(response.text)
  # print(parsed["ids"])
  return(parsed["ids"])

def get_new_following(username, bearer, webhook):
  try:
    id = get_id(username) #pickle this data
    #max amount of followers we can get is 1000, a limitiation set by Twitter API v2, but it gets the most recent 1000 following
    url = url = "https://api.twitter.com/2/users/"+id+"/following"
    payload={}
    headers = {
    'Authorization': bearer,
      'Cookie': 'guest_id=v1%111; personalization_id="111=="'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    current_following = json.loads(response.text)

    if (current_following == {'title': 'Too Many Requests', 'detail': 'Too Many Requests', 'type': 'about:blank', 'status': 429}):
      print("caught errror: too many twitter requests")
      return None

    if (current_following == {'title': 'Service Unavailable', 'detail': 'Service Unavailable', 'type': 'about:blank', 'status': 503}):
      print("caught errror: 503")
      return None

    current_following = current_following["data"]
    ##################
    # pickle_following_import(id, current_following) #forced manual initialise
    ##################
  
    intro_line = False 

    #if already stored in database
    f = open("following.pkl", "rb")
    data = pickle.load(f)
    last_following = data[id]

    # print("lastfollowing: ",last_following)
    if current_following == last_following:
      print(username + " no new following accounts yet")
    else:
      for f in current_following:
        if f in last_following:
          break
        else:
          if intro_line == False:
            print(username, ": is following...")
            webhook.send("**"+username + "\'s** following new accounts:")
            sleep(0.15)
            intro_line = True
          link = " https://twitter.com/" + f['username']
          # add username to sql project_profile
          sql = "INSERT INTO project (username, good) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = VALUES(username);"
          val = (f['username'], 0)
          insert(sql, val)
          sleep(0.15)

          # get current followers count
          followers_count = get_followers_count(f['username'])
          print("Amount of followers",followers_count)
          now = datetime.now()
          now.strftime('%Y-%m-%d %H:%M:%S')

          #add hit information to hit table
          sql = "INSERT INTO hit (twitter_profile_user, project_profile_user, followers_at_time, datetime) VALUES (%s, %s, %s, %s);"
          val = (username, f['username'], followers_count, now)
          insert(sql, val)
          sleep(0.15)
          print(f['username'], "followed by ", username)
          webhook.send(f['username'] + link)
          sleep(0.15)

          # save a snapshot of the followers of the project if project has less than 10,000 followers
          if followers_count <= 10000:
            followers = get_followers(f['username'])
            followers = ','.join(str(f) for f in followers)

            sql = "INSERT INTO snapshot (project_profile_user, number_of_followers, list_of_followers, datetime) VALUES (%s, %s, %s, %s);"
            val = (f['username'], followers_count, followers, now)
            insert(sql, val)

        # db[id] = current_following #update the follower list into the database
        pickle_following_import(id, current_following) #print(either addition or subtraction of a follower, can be used for see who is unfollowing)
  
  #if no key exists
  except KeyError: #make this if sql select is blank
    # db[id] = current_following
    print(traceback.format_exc())
    pickle_following_import(id, current_following)
    print(id, "added to pickle database")
  except json.decoder.JSONDecodeError:
    print("during " + username + " GET call JSONDecodeError occured")
  except TypeError:
    print(traceback.format_exc())
    print(username + "'s databse is corrupt, please reset \n")
    # del db[id]
  except discord.errors.HTTPException:
    webhook.send("Too many discord requests, please reset \n")


# def stalk_all(DISCORD_WEBHOOK, TWITTER_BEARER, cookie, accounts):
def stalk_all(accounts, bearer, webhook):
  # randomised order for when the might be too many twitter requests
  random_order_accounts = accounts
  random.shuffle(random_order_accounts)
  for a in random_order_accounts:
    get_new_following(a, bearer, webhook)
