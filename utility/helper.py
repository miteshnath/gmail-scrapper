import base64
import time
import pickle
import re
import sys
import os.path
import datefinder
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

sys.path.append(os.getcwd())

from config.keywords import KEYWORDS
from config.configurations import (INITIAL_TIMESTAMP, REDIS_HOST, REDIS_PORT, REDIS_DB,
                                      REDIS_PWD, MONGO_COLLECTION, INITIAL_TIMESTAMP)
from .mongo import MongoDb
from .redis import RedisConn


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


def fetch_email(service, words, _timestamp):
    # Call the Gmail API
    query = f"after:{_timestamp}"
    results = service.users().messages().list(userId='me', labelIds=["INBOX"], q=query).execute()
    messages = results.get('messages', [])
    
    if len(messages)<1:
        yield []
    else:
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
            res = {}
            res["body"] = msg['snippet']
            res['created_at'] = int(time.time())
            matches = datefinder.find_dates(res["body"])
            
            for match in matches:
                res["bill_date"] = match
                
            for header in msg['payload']['headers']:
                if 'name' in header.keys() and header['name'] in ["Subject", "From", "To"]:
                    if header.get("name") == "Subject":
                        _type = []
                        match = False
                        for w in words:
                            if re.search(fr'{w}', header.get("value", "").lower()):
                                _type.append(w)
                                match = True
                        if not match:
                            yield []
                        res["type"] = _type
                    res[header["name"]] = header["value"]
            
            try:
                for part in msg['payload']['parts']:
                    if part['filename']:
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(
                            userId="me", messageId=message['id'], id=att_id
                            ).execute()
                        file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                        res["attachment_file"] = part['filename']
                        res["attachment_data"] = str(file_data)
            except KeyError:
                pass                                                 
            
            yield res
            

def fetch_keywords():
        redis_conn = RedisConn(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PWD).get_conn()
        keywords = redis_conn.exists("search_keywords")
        if not keywords:
            redis_conn.sadd("search_keywords", *KEYWORDS)
        return redis_conn.smembers("search_keywords")