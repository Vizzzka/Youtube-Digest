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
    query_job = db_client.query("UPDATE DigestStorage.Users"
                                " SET token = JSON '{}'"
                                " WHERE chat_id = {}".format(creds.to_json(), user_id))
    query_job.result()


def get_all_users_subs(db_client):
    query_job = db_client.query("SELECT chat_id, channel_id token FROM DigestStorage.Subscription")
    result = query_job.result()
    all_users = dict()
    for r in result:
        row = []
        for r2 in r:
            row.append(r2)
        all_users[row[0]] = all_users.get(row[0], [])
        all_users[row[0]].append(row[1])

    return all_users


def store_digests(all_users_dict, bucket_name):
    digests = dict()
    for (key, value) in all_users_dict.items():
        videos_id = []
        for item in value:
            res = get_new_videos_by_channel_id(item)
            ids = filter(lambda x: x["contentDetails"].get("upload", None) != None, res["items"])
            ids = [item["contentDetails"]["upload"]["videoId"] for item in ids]
            videos_id = videos_id + ids
        digests[key] = from_json_to_tg_digest({"videos": [get_digest_by_video_id(video_id) for video_id in videos_id]})
        #store to gcs
        print(digests[key])


def get_digest_by_video_id(video_id):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version)

    request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        maxResults=3,
        id=video_id,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks"
    )
    data = {"name": "", "channel_name": "", "views": "", "number_in_trends": "", "likes": "", "top_comment": "", "link_to_video": ""}
    response = request.execute()
    data["name"] = response["items"][0]["snippet"]["title"]
    data["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][0]["id"])
    data["views"] = response["items"][0]["statistics"]["viewCount"]
    data["likes"] = response["items"][0]["statistics"]["likeCount"]
    data["channel_name"] = response["items"][0]["snippet"]["channelTitle"]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        videoId=response["items"][0]["id"],
        order="relevance"
    )
    try:
        response2 = request.execute()
        data["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
    except:
        pass

    return data


def get_new_videos_by_channel_id(channel_id):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks")

    request = youtube.activities().list(
        part="contentDetails,snippet",
        maxResults=40,
        publishedAfter="2023-06-02T23:00:00.0+02:00",
        channelId=channel_id
    )
    response = request.execute()
    return response


def from_json_to_tg_digest(digest_json):
    result = ""
    for video in digest_json["videos"]:
        s = "\U000027A1  <a href='{}'>{}</a> {} \n \U0001F440 <b>{} views</b> \n \U0001F44D <b> {} likes </b> \n \U0001F525 {} in trends \n \U0001F4E2 <i>{}</i> \n \n".format(video["link_to_video"],
                                   video["name"],
                                   video["channel_name"],
                                   number_of_views(video["views"]),
                                   number_of_views(video["likes"]),
                                   number_in_trend(video["number_in_trends"]),
                                   video["top_comment"])
        result = result + s
    return result


def number_in_trend(number):
    if number is None:
        return "Not"
    else:
        return number


def number_of_views(views):
    print(views)
    views=int(views)
    if views > 1000000:
        return str(views // 1000000) + "M"
    else:
        return str(views / 1000) + "k"


if __name__ == "__main__":
    db_client = bigquery.Client()
    channel_id = "UC6pGDc4bFGD1_36IKv3FnYg"
    credentials_dct = {"client_id":"1066834567857-8flsq25qm601hgibojsjvspetvho8ula.apps.googleusercontent.com","client_secret":"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","expiry":"2023-06-03T19:24:39.023794Z","refresh_token":"1//0eFpy6dD5hJ_0CgYIARAAGA4SNwF-L9IrkQyIrT9zpY6EARZkWtATWmJL4zVyRHjcCopWCyPADhK7qXdymsh91ztO2Y47DnXPXcE","scopes":["https://www.googleapis.com/auth/youtube.readonly"],"token":"ya29.a0AWY7Ckn_dtbUHXC53aD1eEIR9JD4lifhzhUkForG2F3E_cquiyev-O9T2xpFcxgBDzvqrEu6Lywjn9NShOMVRUvVJSgsQRiUw4LfsUXoxDECTIj2--uaDM2ub995frr6BtiLup1kcPrEqTe7TXwSH7Dc_qSPaCgYKAZgSAQ8SFQG1tDrpk8MM8_GNfdp-_pnP-iw9yQ0163","token_uri":"https://oauth2.googleapis.com/token"}
    #get_new_videos_by_channel_id(264147190, channel_id, credentials_dct, db_client)
    store_digests(get_all_users_subs(db_client), "")
    #get_new_videos_by_channel_id('UC6pGDc4bFGD1_36IKv3FnYg')