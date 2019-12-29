FROM python:latest

WORKDIR /app
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh
RUN pip install kafka-python

COPY consumer.py consumer.py
COPY producer.py producer.py

ENTRYPOINT [ "python", "consumer.py" ]