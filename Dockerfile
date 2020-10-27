
FROM python:3.8-slim-buster

WORKDIR /usr/src/app

RUN pip3 install pipenv

COPY . .

RUN pipenv lock --requirements > requirements.txt &&\
    pip3 install -r requirements.txt

CMD ["python3", "bot"]
