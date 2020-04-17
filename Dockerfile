FROM python:3.8

WORKDIR /opt

COPY requirements.txt /opt

RUN pip install -r requirements.txt

COPY . /opt