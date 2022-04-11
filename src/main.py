# Import Python libraries.
from typing import Optional
import argparse

# Import third party libraries.
from codetiming import Timer

# Import local modules.
from src.utils.spark_setup import start_spark
from src.utils.timer_utils import timer_args
from src.dataproc_serverless_airflow.read_file import read_file, retrieve_files
from src.dataproc_serverless_airflow.save_to_bq import save_file_to_bq


def run(app_name: Optional[str],
        known_args) -> None:
    """
    :param app_name: Spark App Name,
    :param known_args: CLI Params
    """

    total_time = Timer(**timer_args("Total run time"))
    total_time.start()

    dataset_name = "serverless_spark_airflow_demo"
    table_name = "stock_prices"

    with Timer(**timer_args('Spark Connection')):
        spark = start_spark(app_name=app_name,
                            bucket=known_args.temp_bq_bucket)

    with Timer(**timer_args('Read File From GCS')):
        files = retrieve_files(known_args=known_args)
        stocks_df = read_file(spark=spark,
                              files=files)

    with Timer(**timer_args('Write DF to Bigquery')):
        status = save_file_to_bq(stocks_df=stocks_df,
                                 table=f'{dataset_name}.{table_name}')

    total_time.stop()
    print(Timer.timers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--project',
        type=str,
        dest='project_id',
        required=True,
        help='GCP Project ID')

    parser.add_argument(
        '--data-bucket',
        type=str,
        dest='data_bucket',
        required=True,
        help='File Source Bucket Location')

    parser.add_argument(
        '--file-names',
        dest='file_names',
        required=True,
        help='Names of the File Separated by Comma , for example, file_name.csv,file_name1.csv')

    parser.add_argument(
        '--temp-bq-bucket',
        type=str,
        dest='temp_bq_bucket',
        required=True,
        help='Name of the Temp GCP Bucket -- DO NOT add the gs:// Prefix')

    known_args, pipeline_args = parser.parse_known_args()

    run(app_name="serverless-spark-airflow-demo",
        known_args=known_args)
