FROM alpine:3.6
LABEL   Name="Redismoke"
LABEL   Maintainer="Bernardo Donadio <bdonadio@stone.com.br>"
ENTRYPOINT [ "/bin/sh", "/opt/redismoke/docker-entrypoint.sh" ]
CMD [ "/etc/redismoke.yml" ]

RUN apk add --update python3 py-pip

WORKDIR /opt/redismoke
COPY requirements.txt /opt/redismoke/
RUN pip3 install -r requirements.txt

COPY docker-entrypoint.sh /opt/redismoke/docker-entrypoint.sh
COPY src /opt/redismoke

LABEL   Version=v2.0.0
