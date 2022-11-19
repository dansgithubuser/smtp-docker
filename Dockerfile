FROM python:3-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /smtp-docker

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server.py .

COPY git-state.txt .

EXPOSE 8025

ENTRYPOINT python3 server.py
