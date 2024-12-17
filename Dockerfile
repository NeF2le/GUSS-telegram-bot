FROM python:3.12
RUN apt-get update && apt-get install -y postgresql-client
WORKDIR /app/GUSS-telegram-bot
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .
COPY . .
