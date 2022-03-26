FROM python:3.8.12-slim

WORKDIR /usr/src/app

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y software-properties-common gnupg \
     && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A6DCF7707EBC211F \
     && apt-add-repository 'deb http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu focal main' \
     && apt-get update && apt-get install firefox -y && apt-get clean

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY libs/common.py libs/dbcontroller.py libs/browser.py libs/validations.py libs/

COPY page_objects/home.py page_objects/homes.py page_objects/index.py \
     page_objects/listing.py page_objects/

COPY browser-info.json .env config.yaml \
     run.py ./
