FROM python:latest

WORKDIR /app
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh
RUN pip install kafka-python flask mysql-connector-python

COPY server.py server.py

ENTRYPOINT [ "python", "server.py" ]