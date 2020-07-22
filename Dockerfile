FROM continuumio/miniconda3

ADD . /app

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install tox && \
    make dev

EXPOSE 8000
