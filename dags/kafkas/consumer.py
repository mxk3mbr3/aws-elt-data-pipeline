# Kafka Imports
import json
from kafka import KafkaConsumer

# Database Imports
from s3fs import S3FileSystem

# Airflow Variables
from airflow.models import Variable

# Global variables
AWS_ACCESS_KEY_ID = Variable.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = Variable.get("AWS_SECRET_ACCESS_KEY")
TOPIC_NAME = "malta_activities"

# Setting up s3 connection
s3 = S3FileSystem(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY)

# Kafka consumer settings
consumer = KafkaConsumer(
    TOPIC_NAME,
    auto_offset_reset="earliest",  # where to start reading the messages at
    group_id=None,  # consumer group id
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda m: json.loads(
        m.decode("utf-8")
    ),  # we deserialize our data from json
    api_version=(1, 4, 6),
    consumer_timeout_ms=5000,  # exit consumer after 5 seconds of not recieving any new messages
)


# Upload data directly from consumer to s3 bucket
def consume_activities():
    # Going through activities in consumer
    for count, activity in enumerate(consumer):
        with s3.open(
            "s3://tripadvisor-activities-malta-project/review_activities_{}.json".format(
                count
            ),
            "w",
        ) as file:
            json.dump(activity.value, file)
