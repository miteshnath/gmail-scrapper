# -- coding: utf-8 --

import os
import sys
import datetime
import time
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask_session import Session

sys.path.append(os.getcwd())

from utility.helper import print_index_table, credentials_to_dict, fetch_email, fetch_keywords
from config.configurations import (CLIENT_SECRETS_FILE, SECRET_KEY,
                                      SCOPES, API_SERVICE_NAME, API_VERSION,
                                        INITIAL_TIMESTAMP, REDIS_HOST, REDIS_PORT, REDIS_DB,
                                      REDIS_PWD, MONGO_COLLECTION, INITIAL_TIMESTAMP, SESSION_REDIS, SESSION_TYPE)
from utility.mongo import MongoDb

app = flask.Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = SESSION_TYPE
app.config['SESSION_REDIS'] = SESSION_REDIS

session = Session()
session.init_app(app)

@app.route('/')
def index():
    return print_index_table()


@app.route('/run-scrapper')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    
    if '_last_timestamp' not in flask.session:
        flask.session['_last_timestamp'] = INITIAL_TIMESTAMP

    words = fetch_keywords()
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    output_db = MongoDb(MONGO_COLLECTION)
    
    insert_ids = []
    for msg in fetch_email(service, words, flask.session['_last_timestamp']):
        if msg:
            if msg['type']:
                msg["created_on"] = datetime.datetime.utcnow()
                insert_ids.append(str(output_db.insert_one(msg)))
            else:
                print(msg['From'])
            
    flask.session['credentials'] = credentials_to_dict(credentials)
    flask.session['_last_timestamp'] = int(time.time())
    return flask.jsonify({"message": "successfully inserted emails to mongo db",
                          "doc_ids": insert_ids})


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    flask.session['state'] = state
    print(flask.session)
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    print(flask.session)
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if '_last_timestamp' in flask.session:
        del flask.session['_last_timestamp']
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())

@app.route('/doc/<id>')
def get_mongo_doc(id):
    output_db = MongoDb(MONGO_COLLECTION)
    res = output_db.find_one({"_id": id})
    res['_id'] = str(res['_id'])
    return flask.jsonify(res), 200


@app.route('/docs/<count>')
def get_docs(count):
    output_db = MongoDb(MONGO_COLLECTION)
    return flask.jsonify(output_db.get_last_n(count)), 200


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('127.0.0.1', 8080, debug=True)
