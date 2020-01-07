FROM python:latest

WORKDIR /app
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh
RUN pip install kafka-python
RUN pip install mysql-connector-python

COPY *.py ./

ENTRYPOINT [ "python", "consumer.py" ]