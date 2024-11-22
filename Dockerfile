FROM python:3.14.0a2-alpine

WORKDIR /app

RUN apk add curl unzip chromium-chromedriver chromium supervisor

COPY . .
COPY infra/supervisord.conf /etc/supervisord.conf

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN mkdir -p /etc/cron.d/ && echo "1 6,18 * * * python /app/scheduler.py" > /etc/cron.d/scraper

RUN crontab /etc/cron.d/scraper
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
