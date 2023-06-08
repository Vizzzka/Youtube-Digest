import os
import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import bigquery
from google.cloud import storage
import json
from datetime import datetime

TG_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


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
        digests[key] = {"videos": [get_digest_by_video_id(video_id) for video_id in videos_id]}
        #store to gcs
    to_gcs(digests)

def to_gcs(digests):
    bucket_name = "youtube-digests"
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    for key, value in digests.items():
        month = datetime.now().month
        day = datetime.now().day
        blob = bucket.blob("2023/{}/{}/digest-{}.json".format(month, day, key))
        blob.upload_from_string(data=json.dumps(value), content_type='application/json')


def get_digest_by_video_id(video_id):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version)

    request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        maxResults=3,
        id=video_id,
        key=GOOGLE_API_KEY
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
        key=GOOGLE_API_KEY,
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
        publishedAfter="2023-06-03T23:00:00.0+02:00",
        channelId=channel_id
    )
    response = request.execute()
    return response


if __name__ == "__main__":
    db_client = bigquery.Client()
    store_digests(get_all_users_subs(db_client), "")