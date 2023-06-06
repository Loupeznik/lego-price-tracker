# Lego price tracker

[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/loupeznik/lego-price-tracker?style=for-the-badge)](https://hub.docker.com/repository/docker/loupeznik/lego-price-tracker)
![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/loupeznik/lego-price-tracker?style=for-the-badge)
![Docker Pulls](https://img.shields.io/docker/pulls/loupeznik/lego-price-tracker?style=for-the-badge)

A simple FastAPI application for tracking prices from [lego.com](https://lego.com). Uses MongoDB for storing data and Slack for alerting. Price fetching runs as a cronjob within the container and scrapes the current prices every 12 hours. Scraping can also be invoked manually via the API. Items to be tracked can be added via the API (see OpenAPI spec).

## Prerequisites
- MongoDB instance
- Slackbot for alerting
- Chromedriver (if used without running in Docker)

## Running

```bash
sudo docker run -p 8000:80 --env-file=.env -d --restart=always --name lego loupeznik/lego-price-tracker:latest
```

.env file should contain the following:

```
MONGO_CONNECTION_STRING=<mongodb_connection_string>
CHROMEDRIVER_PATH=/usr/bin/chromedriver
SLACK_OAUTH_TOKEN=<slackbot_token>
SLACK_CHANNEL_ID=<slack_channel_id>
```

After running, go to http://yourserver.com:8000/docs to see the OpenAPI spec.

## Usage

The application works with *Items* and *Records*. *Items* are objects which will be used for scraping, these contain URLs to be scraped and additional metadata about the item. 
*Records* are used to keep track of item prices and comparing them. After each webscraping job, a new record is created for each item.

To create an item:

```bash
curl --location 'http://127.0.0.1:8000/items' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://www.lego.com/en-us/product/fast-furious-1970-dodge-charger-r-t-76912"
}'
```

A cron job which runs every 12 hours then takes every item and scrapes information about the item from given URL and saves the information including the current price as a new *Record*. 
If the price changes, an alert is sent to Slack.

To get records for an item, call `curl http://127.0.0.1:8000/records/{set_id}`.

## Roadmap
- Authentication
- Making alerting optional
- Better filtering
