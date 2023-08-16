# Locally: 
# Run the below command to create an extended image using Dockerfile:
# docker build . -f Dockerfile --pull --tag extending-image
# Then use this image (extending-image) in the docker compose file

# Using Github Actions:
# Use Dockerfile and push image to Docker Hub
# Reference image in docker compose file under 'image' environment i.e.
# image: ${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}

# AIRFLOW_HOME=/opt/airflow is the default
ARG  AIRFLOW_VERSION=2.5.3

FROM apache/airflow:${AIRFLOW_VERSION}-python3.9

ENV AIRFLOW_HOME=/opt/airflow

COPY requirements.txt /

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt