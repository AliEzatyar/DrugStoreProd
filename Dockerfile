FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --upgrade pip

ENV PIP_NO_CACHE_DIR=1

RUN pip install -r requirements.txt

COPY . /code/

