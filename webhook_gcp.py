from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import google_auth_oauthlib.flow
from urllib.parse import urlparse
from urllib.parse import parse_qs
from google.cloud import bigquery
from datetime import datetime
import os
import requests


app = FastAPI()

TG_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")

@app.get("/")
async def main(request: Request):
    authorization_response = request.url._url
    parsed_url = urlparse(request.url._url)
    chat_id = parse_qs(parsed_url.query)['state'][0]

    client = bigquery.Client()
    query_job = client.query("SELECT chat_id FROM DigestStorage.Users WHERE chat_id={}".format(chat_id))
    res = query_job.result()
    if res.num_results() != 0:
        res = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(TG_TOKEN),
                            headers={
                                'Content-type': 'application/json'
                            },
                            json={"chat_id": str(chat_id), "text": "You are already registered",
                                  "disable_notification": False}, )
        return RedirectResponse("https://t.me/youtube_videos_digest_bot")

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
           'client_secret_1066834567857-8flsq25qm601hgibojsjvspetvho8ula.apps.googleusercontent.com.json',
           scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        flow.redirect_uri = 'https://youtubedigestapp.de.r.appspot.com'
        flow.fetch_token(authorization_response=authorization_response)


        credentials = flow.credentials
        #store token & client id
        print(credentials.to_json())

        client = bigquery.Client()
        query_job = client.query(""
                             "INSERT `DigestStorage.Users` (chat_id, youtube_id, is_active, subscription_date, token)"
                             " VALUES({}, '{}', {}, '{}', JSON '{}')"
                             .format(chat_id, credentials.client_id, True, str(datetime.now())[:18], credentials.to_json()))


        results = query_job.result("".format(chat_id, True))
        res = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(TG_TOKEN),
                            headers={
                                'Content-type': 'application/json'
                            },
                            json={"chat_id": str(chat_id), "text": "You are successfully logged-in",
                                  "disable_notification": False}, )
        print(res.text)
    except:
        requests.post('https://api.telegram.org/bot{}/sendMessage'.format(TG_TOKEN),
                      headers={
                          'Content-type': 'application/json'
                      },
                      json={"chat_id": str(chat_id), "text": "You are not registered. Try again.",
                            "disable_notification": False}, )

    return RedirectResponse("https://t.me/youtube_videos_digest_bot")
