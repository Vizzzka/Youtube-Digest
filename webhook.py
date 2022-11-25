from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import google_auth_oauthlib.flow
from cassandra.cluster import Cluster
import urllib.parse

app = FastAPI()

@app.get("/")
async def main(request: Request):
    authorization_response = request.url._url
    code = authorization_response.split('&')[1][5:]
    chat_id = authorization_response.split('&')[0].split('=')[1]
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret_668784317009-a22cokals81donercshr929k6hl1h967.apps.googleusercontent.com.json',
        scopes=["https://www.googleapis.com/auth/youtube.readonly"])
    flow.redirect_uri = 'http://localhost:8000/'

    decoded = urllib.parse.unquote(code)
    flow.fetch_token(code=decoded)
    credentials = flow.credentials
    #store token & client id
    clstr = Cluster()
    session = clstr.connect('simplex')
    print(chat_id)
    print(credentials.client_id)
    print(credentials.token)
    print(credentials.refresh_token)
    print(credentials.client_secret)
    session.execute(
        "insert into users_channels (chat_id, client_id, access_token, refresh_token) values ({0},'{1}','{2}','{3}');"
            .format(chat_id, credentials.client_id, credentials.token, credentials.refresh_token))
    return RedirectResponse("https://t.me/youtube_videos_digest_bot")
