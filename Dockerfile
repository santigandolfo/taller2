FROM ubuntu:latest
MAINTAINER Taller2 Team APGB

RUN apt-get update
RUN apt-get install -y build-essential python-pip
RUN pip install --upgrade pip


ENV ENV DEV

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE  5000

CMD ["/app/start.sh"] 


