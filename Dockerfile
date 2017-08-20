FROM ubuntu:latest
MAINTAINER Taller2 Team APGB

RUN apt-get update
RUN apt-get install -y build-essential python-pip
RUN pip install --upgrade pip

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["/app/start.sh"] 
