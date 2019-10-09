# FROM python:3.7-alpine3.7
# LABEL maintainer="Dheeraj Kumar Joshi<dheerajkrjoshi3@gmail.com>"
FROM ubuntu:18.04
LABEL maintainer="Dheeraj Kumar Joshi<dheerajkrjoshi3@gmail.com>"
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends apt-utils\
    software-properties-common \
    python3-setuptools \
    python3-pip \
    python3-wheel \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev
RUN mkdir /src
WORKDIR /src
COPY ./src/app.py .
COPY ./src//config.yaml .
COPY ./src/requirements.txt .
RUN pip3 install -r requirements.txt && chmod +x app.py
EXPOSE 8080
ENTRYPOINT ["python3", "app.py", "--config", "config.yaml"]
