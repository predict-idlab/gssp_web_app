FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apt update && apt install --reinstall -y ca-certificates
RUN curl https://rclone.org/install.sh | bash

COPY ./requirements.txt /
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -U -r /requirements.txt

ENV NGINX_MAX_UPLOAD 30m

COPY ./app /app
RUN mkdir -p /data/semi_guided_speech/
