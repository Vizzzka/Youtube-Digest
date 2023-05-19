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

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def update_creds(user_id, creds, db_client):
    query_job = db_client.query("UPDATE `test_youtube_digest.Users`"
                                " SET credentials = JSON '{}'"
                                " WHERE chat_id = {}".format(creds.to_json(), user_id))
    query_job.result()


def get_new_videos_by_channel_id(user_id, channel_id, credentials_dct, db_client):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_1066834567857-8flsq25qm601hgibojsjvspetvho8ula.apps.googleusercontent.com.json"
    creds = Credentials.from_authorized_user_info(credentials_dct, scopes)
    if True:
        creds.refresh(Request())
        #write cred to db
        update_creds(user_id, creds, db_client)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)

    request = youtube.activities().list(
        part="contentDetails,snippet",
        maxResults=40,
        publishedAfter="2022-12-19T23:00:00.0+02:00",
        channelId=channel_id
    )
    response = request.execute()
    print(response)
    return response


def store_videos(response, db_client):
    pass


if __name__ == "__main__":
    db_client = bigquery.Client()
    channel_id = "UC6pGDc4bFGD1_36IKv3FnYg"
    credentials_dct = {"client_id":"668784317009-a22cokals81donercshr929k6hl1h967.apps.googleusercontent.com","client_secret":"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","expiry":"2022-12-19T05:12:44.529431Z","refresh_token":"1//0917dx22Er2qfCgYIARAAGAkSNwF-L9Iro-2F0Zr_MrQ2LuTIpt88s0__i0T4pjUOlMlXEev-LkgvswYf3HJOodDl5Xycfo35a58","scopes":["https://www.googleapis.com/auth/youtube.readonly"],"token":"ya29.a0AX9GBdWo4LDRD9H9CmFz6IhqV9T1Cs8AdspicwTOvpP3KeADfn3oB-Z8PcFaL3Pa2pA0Cq0BGg3aAHi8m6SA4jDFE6pTiromGTEy-e1EdJt6YQW5h3AlUKq5WQwBytV6tqNzrbaUhOtT1Ae-EK-6rAYyR0LkhvEaCgYKAVwSAQASFQHUCsbCYjpVNh3CcGpDlrqKUe0pDw0166","token_uri":"https://oauth2.googleapis.com/token"}
    get_new_videos_by_channel_id(264147190, channel_id, credentials_dct, db_client)