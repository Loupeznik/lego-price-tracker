import logging
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

import db.database
from db.item import Item
from db.record import Record

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1420,1080")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(os.environ["CHROMEDRIVER_PATH"])
    return webdriver.Chrome(options=options, service=service)


async def scrape(item: Item, driver: webdriver.Chrome) -> Record or bool:
    driver.get(item.url)

    try:
        WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.CLASS_NAME, "epIXnJ"))
        )
    except TimeoutException:
        print("Timed out waiting for page to load")
        logging.log(logging.ERROR, "Timed out waiting for page to load")
        driver.quit()
        return False

    try:
        is_item_updated = False

        name = driver.find_element("xpath", "/html/body/div[1]/div/main/div/div[1]/div/div[2]/div[2]/h1/span").text
        _price = driver.find_element("xpath", "/html/body/div[1]/div/main/div/div[1]/div/div[2]/div[3]/div/span").text

        _price = _price.replace("Price\n", "")
        price, currency = split_currency_string(_price)
        set_id = get_set_id_from_url(item.url)

        record = Record(name=name, url=item.url, price=price, currency=currency, set_id=set_id)

        await record.create()

        if item.name is None:
            item.name = name
            is_item_updated = True

        if item.set_id is None:
            item.set_id = set_id
            is_item_updated = True

        if is_item_updated:
            await item.save()

        return record
    except Exception as e:
        logging.log(logging.ERROR, e)
        return False


def split_currency_string(currency_string: str) -> tuple[float, str]:
    pattern = r'([\d.,]+)(\D+)'

    match = re.match(pattern, currency_string)

    if match:
        numeric_part = match.group(1)
        non_numeric_part = match.group(2)

        return float(numeric_part.replace(",", ".")), non_numeric_part.strip(" ")
    else:
        return 0.00, ""


def get_set_id_from_url(url: str) -> int or None:
    match = re.search(r'\d+$', url)

    if match:
        last_part = match.group(0)

        return int(last_part)

    return None


def send_slack_message(message: str, is_lower: bool):
    slack_token = os.environ["SLACK_OAUTH_TOKEN"]

    client = WebClient(token=slack_token)

    icon = ":chart_with_downwards_trend:" if is_lower else ":chart_with_upwards_trend:"

    try:
        client.chat_postMessage(
            channel=os.environ["SLACK_CHANNEL_ID"],
            text=f"{icon} {message}"
        )
    except SlackApiError as e:
        logging.log(logging.ERROR, f"Got an error: {e.response['error']}")


async def run_scraper(driver: webdriver.Chrome):
    items = await db.database.get_items()
    for item in items:
        previous_record = await Record.find_one({"url": item.url}, sort=[("date", -1)])
        result = await scrape(item, driver)
        if isinstance(result, Record):
            if previous_record is not None:
                if previous_record.price != result.price:
                    message = \
                        f"Price of {result.name} changed from {previous_record.currency}{previous_record.price} " \
                        f"to {result.currency}{result.price}"
                    send_slack_message(message, result.price < previous_record.price)
