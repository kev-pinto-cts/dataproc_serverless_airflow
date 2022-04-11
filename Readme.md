# Packaging and Running a PySpark Job On Google's Serverless Spark Service

### Pre-reqs
* Install [Python Poetry](https://python-poetry.org/docs/)


<h3 id="folder-structure"> :file_folder: Folder Structure</h3>

```shell
.
├── LICENSE
├── Makefile
├── Readme.md
├── dags
│   ├── __init__.py
│   ├── event_based_dataproc_serverless_pipeline.py
│   └── utils
│       ├── __init__.py
│       └── cleanup.py
├── dist (temp folder for packaging)
│   ├── dataproc_serverless_airflow_0.1.0.zip
│   └── main.py
├── poetry.lock
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── dataproc_serverless_airflow
│   │   ├── __init__.py
│   │   ├── read_file.py
│   │   └── save_to_bq.py
│   ├── main.py
│   └── utils
│       ├── __init__.py
│       ├── spark_setup.py
│       └── timer_utils.py
├── stocks.csv
└── stocks1.csv

```

### Setup the Example in GCP (Run Once Only)
Edit the `Makefile` and change the following 2 params
```shell
PROJECT_ID ?= <CHANGEME>
REGION ?= <CHANGEME>
DAG_BUCKET ?= <CHANGEME>

#for example
PROJECT_ID ?= my-gcp-project-1234
REGION ?= europe-west2
DAG_BUCKET ?= my-bucket
```

Then run the following command from the Root Folder of this Repo
```shell
make setup
```

This will create the following:
* GCS Bucket `serverless-spark-airflow-code-repo-<PROJECT_NUMBER>` →Our Pyspark Code gets uploaded here
* GCS Bucket `serverless-spark-airflow-staging-<PROJECT_NUMBER>` →Used for BQ operations
* GCS Bucket `serverless-spark-airflow-data-<PROJECT_NUMBER>` → Our source csv file is in here 
* Bigquery Dataset called `serverless_spark_airflow_demo` in BigQuery


### Packaging you Pipeline for GCP
```shell
make build
```

### Deploy Dag to cloud composer
```shell
make dags
```