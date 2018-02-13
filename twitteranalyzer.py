import sys
import requests
import json
import tweepy
import config
import time
import calendar

def convert_status_to_pi_content_item(s):
    # My code here
    return {
        'userid': str(s.user.id),
        'id': str(s.id),
        'sourceid': 'python-twitter',
        'contenttype': 'text/plain',
        'language': s.lang,
        'content': s.text,
        'reply': (s.in_reply_to_status_id == None),
        'forward': False
    }


handle = sys.argv[1]

# Twitter Credentials
#
# To obtain the credentials, you must first have a Twitter account. 
# Then, go to https://dev.twitter.com/, login, and click on "Manage Your Apps" to reach https://apps.twitter.com/.
# Then, click "Create New App", fill in the relevant fields, and click "Create your Twitter application".
# With the application created, navigate to the API Keys page and click "Create my access token". 
# You now have the four necessary credentials. Copy the API key, API secret, 
# Access token, and Access token secret here.
# NOTE: API key and API secret go in the twitter_consumer_key and twitter_consumer_secret vars.
#

access_key=""
access_secret=""
consumer_key=""
consumer_secret=""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

twitter_api = tweepy.API(auth)

max_id = None
statuses = []

for x in range(0, 16):  # Pulls max number of tweets from an account
    if x == 0:
        statuses_portion = twitter_api.user_timeline(screen_name=handle,
                                                       count=200,
                                                       include_rts=False)
        status_count = len(statuses_portion)
        max_id = statuses_portion[status_count - 1].id - 1  # get id of last tweet and bump below for next tweet set
    else:
        statuses_portion = twitter_api.user_timeline(screen_name=handle,
                                                       count=200,
                                                       max_id=max_id,
                                                       include_rts=False)
        status_count = len(statuses_portion)
        print status_count
        try:
            max_id = statuses_portion[status_count - 1].id - 1  # get id of last tweet and bump below for next tweet set
        except:
            pass
    for status in statuses_portion:
        statuses.append(status)

print 'Number of Tweets user have: '+str(len(statuses))

pi_content_items_array = map(convert_status_to_pi_content_item, statuses)
pi_content_items = {'contentItems': pi_content_items_array}

# Personality Insights credentials and URL
#
# You can obtain these credentials by binding a PI service to an application in bluemix and 
# and clicking the "show credentials" link on the service in the application dashboard.
# Or you can use "cf env <application name>" from the command line to get the credentials.

pi_url = ''
pi_username = ''
pi_password = ''

r = requests.post(pi_url + '/v2/profile',
                  auth=(pi_username, pi_password),
                  headers={
                      'content-type': 'application/json',
                      'accept': 'application/json'
                  },
                  data=json.dumps(pi_content_items)
                  )

print("Profile Request sent. Status code: %d, content-type: %s" % (r.status_code, r.headers['content-type']))
print json.loads(r.text)
