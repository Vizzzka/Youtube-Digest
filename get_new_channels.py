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
from datetime import datetime
from datetime import timedelta
from utils import *
import schedule
import time

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client = bigquery.Client()


def create_subscription(user_id, channel_id, title, subDate, registration_date, db_client):
    subDate = subDate.replace("T", " ")[:19]
    sub_d = datetime.strptime(subDate, "%Y-%m-%d %H:%M:%S")
    if registration_date + timedelta(hours=24) > datetime.now() or sub_d + timedelta(hours=24) > datetime.now():
        query_job = db_client.query("INSERT `DigestStorage.Subscription` (chat_id, channel_id, is_active, subscription_date, channel_title)"
                                " VALUES('{}', '{}', {}, '{}', '{}')".format(user_id, channel_id, True, subDate, title))
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


def get_channels_for_all_users():
    query_job = client.query("SELECT chat_id, token, subscription_date FROM DigestStorage.Users")
    result = query_job.result()
    for r in result:
        row = []
        for r2 in r:
            row.append(r2)
        items = get_new_channels_by_user_id(row[0], json.loads(row[1]), client)["items"]
        for item in items:
            create_subscription(row[0], item["snippet"]["resourceId"]["channelId"],
                                item["snippet"]["title"], item["snippet"]["publishedAt"], row[2], client)


if __name__ == "__main__":
    schedule.every().day.at("18:00").do(get_channels_for_all_users)
    while True:
        schedule.run_pending()
        time.sleep(1)