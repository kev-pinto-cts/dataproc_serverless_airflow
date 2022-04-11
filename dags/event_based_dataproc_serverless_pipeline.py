# Standard Imports
from datetime import timedelta
from uuid import uuid1
from pathlib import Path

# Third Party Imports
from airflow.decorators import task, dag
from airflow.utils.dates import days_ago
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStoragePrefixSensor
from airflow.operators.dummy import DummyOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.utils.credentials_provider import get_credentials_and_project_id

# Local Imports
from utils.cleanup import cleanup_xcom

default_args = {
    'start_date': days_ago(1),
    'schedule_interval': '@daily',
    'dagrun_timeout': timedelta(minutes=10),
    'catchup': False,
    'max_active_runs': 1,
    'tags': ["Dataproc Serverless"],
    'retries': 0
}

PROJECT_NUMBER = '1056414501493'
REGION = 'europe-west2'

PREFIX = 'stocks'
DATASET = 'serverless_spark_airflow_demo'
DATA_BUCKET = f'serverless-spark-airflow-data-{PROJECT_NUMBER}'
CODE_BUCKET = f'serverless-spark-airflow-code-repo-{PROJECT_NUMBER}'
STAGING_BUCKET = f'serverless-spark-airflow-staging-{PROJECT_NUMBER}'


# https://cloud.google.com/dataproc-serverless/docs/reference/rpc/google.cloud.dataproc.v1#google.cloud.dataproc.v1.PySparkBatch
@task.python(trigger_rule='all_done')
def cleanup(**kwargs):
    cleanup_xcom(**kwargs)


@task.python(task_id="format_file_names")
def format_file_names(**kwargs):
    dag_id = kwargs['dag'].dag_id
    file_xcom = kwargs['ti'].xcom_pull(task_ids='file_sensor', dag_id=dag_id)
    kwargs['ti'].xcom_push(key='source_files', value=','.join(file_xcom))


@dag(dag_id=Path(__file__).stem,
     description="GCS Sensor",
     default_args=default_args)
def dag_main():
    run_id = str(uuid1())
    _, project_id = get_credentials_and_project_id()

    start = DummyOperator(task_id="start")
    file_sensor = GoogleCloudStoragePrefixSensor(
        task_id='file_sensor',
        bucket=DATA_BUCKET,
        prefix=PREFIX,
        mode="reschedule"
    )

    run_dataproc_serverless_batch = DataprocCreateBatchOperator(
        task_id="run_dataproc_serverless_batch",
        project_id=project_id,
        region=REGION,
        batch_id=f"{PREFIX}-{run_id}",
        batch={
            'pyspark_batch':
                {
                    'main_python_file_uri': f'gs://{CODE_BUCKET}/dist/main.py',
                    'python_file_uris': [f'gs://{CODE_BUCKET}/dist/dataproc_serverless_airflow_0.1.0.zip'],
                    'jar_file_uris': ['gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar'],
                    'args': [f'--project={project_id}',
                             f'--data-bucket={DATA_BUCKET}',
                             '--file-names=' + "{{ task_instance.xcom_pull(task_ids='format_file_names', key='source_files', dag_id='event_based_dataproc_serverless_pipeline') }}",
                             f'--temp-bq-bucket={STAGING_BUCKET}'
                            ]
                },
            'environment_config':
                {'execution_config':
                     {'subnetwork_uri': 'default'}
                 },
            'runtime_config':
                {'properties':
                    {
                        'spark.app.name': 'DataprocServerlessViaAirflow'
                    }
                }
        }
    )
    end = DummyOperator(task_id="end", trigger_rule='all_done')

    start >> file_sensor >> format_file_names() >> run_dataproc_serverless_batch >> cleanup() >> end


# Invoke DAG
dag = dag_main()
