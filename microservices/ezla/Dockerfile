FROM python:3.6-slim
COPY app /srv/flask_app
WORKDIR /srv/flask_app
RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install python3-dev \
    && apt-get -y install build-essential
RUN pip install -r deps.txt --src /usr/local/src
RUN chmod +x ./start.sh
CMD ["./start.sh"]
