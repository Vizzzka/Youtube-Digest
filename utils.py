def update_creds(user_id, creds, db_client):
    query_job = db_client.query("UPDATE `DigestStorage.Users`"
                                " SET token = JSON '{}'"
                                " WHERE chat_id = {}".format(creds.to_json(), user_id))
    query_job.result()


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


def number_of_views(views):
    views=int(views)
    if views > 1000000:
        return str(views // 1000000) + "M"
    else:
        return str(views / 1000) + "k"


def number_in_trend(number):
    if number is None:
        return "Not"
    else:
        return number