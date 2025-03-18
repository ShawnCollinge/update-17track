FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git cron && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN git clone https://github.com/ShawnCollinge/update-17track.git /app

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python3", "main.py"]