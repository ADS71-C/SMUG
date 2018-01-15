FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY resources resources
COPY smug smug

ENV PYTHONPATH=/usr/src/app
