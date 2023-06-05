from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from send_digest import send_digest
import datetime


default_dag_args = {
    'start_date': datetime.datetime(2018, 1, 1),
    'schedule_interval': '0 0 20 * *'
}

gs_bucket = "youtube-digests"

with models.DAG(
        'composer_send-and-archive-digest',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:

    send_digest_python = python_operator.PythonOperator(
        task_id='send-digest-to-users',
        python_callable=send_digest)

    archive_digests = GCSToGCSOperator(
        task_id="archive_digests",
        source_bucket=f'{gs_bucket}',
        source_object="2023/06/05/*.json",
        destination_bucket=f'{gs_bucket}',
        destination_object="2023/06/05/*.json",
        move_object=True
    )

    send_digest_python >> archive_digests