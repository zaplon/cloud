FROM python:3.6

RUN apt-get update -y && apt-get install -y libxml2 xmlsec1 libxml2-dev libxmlsec1-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "run.py" ]
