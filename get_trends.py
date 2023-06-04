import googleapiclient.discovery
import googleapiclient.errors



if __name__ == "__main__":
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version)

    request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        maxResults=3,
        chart="mostPopular",
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        regionCode="UA"
    )
    data = {"videos": [{"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "",
                        "top_comment": "", "link_to_video": ""}]}

    response = request.execute()
    data["videos"][0]["name"] = response["items"][0]["snippet"]["title"]
    data["videos"][1]["name"] = response["items"][1]["snippet"]["title"]
    data["videos"][2]["name"] = response["items"][2]["snippet"]["title"]

    data["videos"][0]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][0]["id"])
    data["videos"][1]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][1]["id"])
    data["videos"][2]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][2]["id"])

    data["videos"][0]["views"] = response["items"][0]["statistics"]["viewCount"]
    data["videos"][0]["likes"] = response["items"][0]["statistics"]["likeCount"]
    data["videos"][1]["views"] = response["items"][1]["statistics"]["viewCount"]
    data["videos"][1]["likes"] = response["items"][1]["statistics"]["likeCount"]
    data["videos"][2]["views"] = response["items"][2]["statistics"]["viewCount"]
    data["videos"][2]["likes"] = response["items"][2]["statistics"]["likeCount"]

    data["videos"][0]["channel_name"] = response["items"][0]["snippet"]["channelTitle"]
    data["videos"][1]["channel_name"] = response["items"][0]["snippet"]["channelTitle"]
    data["videos"][2]["channel_name"] = response["items"][0]["snippet"]["channelTitle"]


    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        videoId=response["items"][2]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][0]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

    print(response2)