from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from get_new_videos import get_and_store_digests
from get_new_channels import get_channels_for_all_users
import datetime


default_dag_args = {
    'start_date': datetime.datetime(2018, 1, 1),
    'schedule_interval': '0 0 19 * *'
}

gs_bucket = "youtube-digests"

with models.DAG(
        'create_and_store_digest',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:

    update_subscriptions_python = python_operator.PythonOperator(
        task_id='update-subscriptions',
        python_callable=get_channels_for_all_users)

    create_digests_python = python_operator.PythonOperator(
        task_id='create-digests',
        python_callable=get_and_store_digests)


    update_subscriptions_python >> create_digests_python