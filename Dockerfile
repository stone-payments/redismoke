FROM alpine

RUN apk add --update python3 py-pip
COPY src /opt/redismoke

WORKDIR /opt/redismoke
RUN pip3 install -r requirements.txt
