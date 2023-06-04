# -*- coding: utf-8 -*-

# Sample Python code for youtube.subscriptions.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
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


def create_subscription(user_id, channel_id, title, subDate, db_client):
    query_job = db_client.query("INSERT `DigestStorage.Subscription` (chat_id, channel_id, is_active, subscription_date, channel_title)"
                                " VALUES('{}', '{}', {}, '{}', '{}')".format(user_id, channel_id, True, subDate.replace("T", " ")[:18], title))
    query_job.result()


def get_new_channels_by_user_id(user_id, credentials_dct, db_client):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    creds = Credentials.from_authorized_user_info(credentials_dct, scopes)
    if creds.expired:
        print("expired")
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
    return response


def get_channels_for_all_users(db_client):
    query_job = db_client.query("SELECT chat_id, token FROM DigestStorage.Users")
    result = query_job.result()
    for r in result:
        row = []
        for r2 in r:
            row.append(r2)
        items = get_new_channels_by_user_id(row[0], json.loads(row[1]), db_client)["items"]
        print(items)
        for item in items:
            create_subscription(row[0], item["snippet"]["resourceId"]["channelId"],
                                item["snippet"]["title"], item["snippet"]["publishedAt"], db_client)


if __name__ == "__main__":
    client = bigquery.Client()
    get_channels_for_all_users(client)