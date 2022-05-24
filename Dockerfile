FROM python:3.9.6

USER root

RUN apt-get install -y curl && \
    apt-get update && apt-get install -y \
    python3.9-dev default-mysql-client default-libmysqlclient-dev iputils-ping dnsutils \
    zip silversearcher-ag telnet lsof tree openssh-client apache2-utils git git-lfs tig && \
    apt-get clean

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.9

RUN mkdir -p /usr/src

WORKDIR /usr/src

COPY requirements.txt requirements-dev.txt /usr/src/

RUN python3.9 -m pip install -r requirements.txt -r requirements-dev.txt

COPY . /usr/src/

CMD ["python", "comment/main.py"]
