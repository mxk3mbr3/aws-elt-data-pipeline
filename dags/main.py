from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from kafkas.producer import produce_activities
from kafkas.consumer import consume_activities

# DAG Global Variables

with DAG(
    dag_id="activities_etl",
    start_date=datetime(2023, 1, 1),
    schedule="@weekly",
    description="Showcasing use of web scraping, kafka and aws to get the activities list on Trip Advisor for Malta",
    tags=["etl", "activities", "web scrape", "kafka", "aws"],
    catchup=False,
):
    # Kafka producer
    producer_activities = PythonOperator(
        task_id="producer_activities",
        python_callable=produce_activities,
    )

    # Kafka consumer
    consumer_activities = PythonOperator(
        task_id="consumer_activities",
        python_callable=consume_activities,
    )

    ############################ Creating DAG dependencies ############################

    [producer_activities >> consumer_activities]
