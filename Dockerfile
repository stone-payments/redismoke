FROM alpine

LABEL   Name="Redismoke" \
        Version="0.1"
ENTRYPOINT [ "/usr/bin/python3", "/opt/redismoke/redismoke.py" ]
CMD [ "/etc/redismoke.yml" ]

RUN apk add --update python3 py-pip

WORKDIR /opt/redismoke
COPY requirements.txt /opt/redismoke/
RUN pip3 install -r requirements.txt

COPY src /opt/redismoke

