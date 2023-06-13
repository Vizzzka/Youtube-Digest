# Youtube-Digest

Get Youtube digests from your subscriptions and currently trending videos via telegram!

This project is intended to be a playground for GCP services. The bot task is simple:
it gets your permission to get youtube subscriptions and then daily sends digests with new videos from subscriptions.
Digest consists of the most popular videos and basic information about them. Also, it is possible to get currently trending videos. 

Try it out: https://t.me/youtube_videos_digest_bot

# General architecture
The app is designed keeping in mind further development in the analytical direction. BigQuery is the main storage with all the historical data regarding users' subscriptions. While a couple of scheduled jobs running in the Cloud Composer environment perform the main processing of creation and storing digests on GCS. The App Engine platform is used to run auxiliary python applications. This way 

# Repository structure
* telegram_bot: reads messages from telegram, redirects to Google authentification 
* webhook: stores user in a database after authentification
* create_digest_DAG: Airflow DAG to update users' subs and create digests in JSON format
* send_digest_DAG: Airflow DAG to send ready digests to telegram chats and archive JSON files on GCS

# Configuration
