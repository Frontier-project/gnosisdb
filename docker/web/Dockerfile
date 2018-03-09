FROM python:3-alpine3.7

RUN mkdir -p /root/var/run/celery
WORKDIR /gnosisdb

COPY requirements.txt ./

# Signal handling for PID1 https://github.com/krallin/tini
RUN apk add --update --no-cache tini postgresql-client && \
    apk add --no-cache --virtual build-dependencies postgresql-dev alpine-sdk libffi-dev autoconf automake libtool && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-dependencies && \
    find /usr/local/lib/ -name '*.pyc' -delete

COPY . ./

ENTRYPOINT ["/sbin/tini", "--"]
