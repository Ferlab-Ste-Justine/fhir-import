FROM python:3.8

WORKDIR /opt

COPY requirements.txt /opt

RUN pip install -r requirements.txt

COPY . /opt

ENV MODEL_GIT_REFERENCE b413ee5833934e572141328f13ab4b02679ef77b
ENV FAULT_TOLERANT false