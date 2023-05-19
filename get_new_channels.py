# -*- coding: utf-8 -*-

# Sample Python code for youtube.subscriptions.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import bigquery
import json


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def update_creds(user_id, creds, db_client):
    query_job = db_client.query("UPDATE `DigestStorage.Users`"
                                " SET token = JSON '{}'"
                                " WHERE chat_id = {}".format(creds.to_json(), user_id))
    query_job.result()


def get_new_channels_by_user_id(user_id, credentials_dct, db_client):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_668784317009-a22cokals81donercshr929k6hl1h967.apps.googleusercontent.com.json"
    creds = Credentials.from_authorized_user_info(credentials_dct, scopes)
    if True:
        creds.refresh(Request())
        #write cred to db
        update_creds(user_id, creds, db_client)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)

    request = youtube.subscriptions().list(
        part="snippet",
        maxResults=40,
        mine=True
    )
    response = request.execute()
    print(response)
    return response


def get_channels_for_all_users(db_client):
    query_job = db_client.query("SELECT chat_id, token FROM DigestStorage.Users")
    result = query_job.result()
    for r in result:
        row = []
        for r2 in r:
            row.append(r2)
        items = get_new_channels_by_user_id(row[0], json.loads(row[1]), db_client)["items"]
        #query_job = db_client.query()



if __name__ == "__main__":
    client = bigquery.Client()
    credentials_dct = {"client_id":"1066834567857-8flsq25qm601hgibojsjvspetvho8ula.apps.googleusercontent.com","client_secret":"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","expiry":"2023-05-17T12:55:59.634012Z","scopes":["https://www.googleapis.com/auth/youtube.readonly"],"token":"ya29.a0AWY7Ckn0D0a13Y4Z_VP_5xi6p-FwjrvOe4OHnh_d485pKApWT5M-VplZZ12qljHVxyac-mrGLQ9QRcW9Uh8nEZ1-o-JZ3_5IAm4393x_mTQz7pbVLtu7sAG5EiTWkOChCSj14fC2l9WkQuiCtg3FMMrmjdBl-QaCgYKAU8SARASFQG1tDrpnYq8p5FcEeZa71BpCB9_rA0165","token_uri":"https://oauth2.googleapis.com/token"}
    #channels = get_new_channels_by_user_id(264147190, credentials_dct, client)
    get_channels_for_all_users(client)