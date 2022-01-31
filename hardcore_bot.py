import os.path
import random
import json
from datetime import date
import tweepy
import os

## google tools

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

##############################################
##
## Google authentication
##
##############################################

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = '1C588DhrV-jd3CGvNgRFy8_jUx_wLk5NaFl1L7sOepCI'
sheet_range_name = 'Sheet1!A2:H'

creds_json = {"token" : os.environ["GOOGLE_TOKEN"], 
              "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"], 
              "token_uri": "https://oauth2.googleapis.com/token", 
              "client_id": os.environ["GOOGLE_CLIENT_ID"], 
              "client_secret": os.environ["GOOGLE_CLIENT_SECRET"], 
              "scopes": ["https://www.googleapis.com/auth/spreadsheets"], 
              "expiry": "2022-01-20T23:43:54.991262Z"}

creds = Credentials.from_authorized_user_info(creds_json, SCOPES)

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=spreadsheet_id,
                            range=sheet_range_name).execute()
values = result.get('values', [])

##############################################
##
## Twitter authentication
##
##############################################

auth = tweepy.OAuthHandler(os.environ["API_KEY"], os.environ["TWITTER_API_KEY"])
auth.set_access_token(os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"])

api = tweepy.API(auth)

##############################################
##
## Form Tweet
##
##############################################

## pick random entry -- but let's see if it's already been tweeted

already_tweeted = 0

while already_tweeted == 0:  
    pick = random.randrange(0,len(values))
    already_tweeted = values[pick][6]

## send first tweet -- out of context hardcore quote

initial_tweet = api.update_status(values[pick][2])

## send follow up tweet with artist name + song name & link for context

folowup_tweet = api.update_status("Describing {} by {} | Link: {}".format(values[pick][1],values[pick][0],values[pick][3]),
                    in_reply_to_status_id=initial_tweet.id)

##############################################
##
## update google sheet to reflect lyric has been tweeted
##
##############################################

batch_update_values_request_body = {
    "valueInputOption": "RAW",
    "data": [
        {
            'range': 'Sheet1!G{}'.format(pick+2),
            'values': [[1]]
        },
        {
            'range': 'Sheet1!H{}'.format(pick+2),
            'values': [[date.today().strftime("%Y/%m/%d")]]
        }
    ]
}

service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, 
                                            body=batch_update_values_request_body).execute()


# end
