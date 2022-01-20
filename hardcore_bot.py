import os.path
import random
import json
from datetime import date
import tweepy

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

try:
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
except:
    creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
else:
    exit

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

with open('twitter_creds.json') as json_file:
    data = json.load(json_file)

auth = tweepy.OAuthHandler(data['API Key'], data['API Key Secret'])
auth.set_access_token(data['Access Token'], data['Access Token Secret'])

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
