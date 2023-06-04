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


def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1420,1080")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(os.environ["CHROMEDRIVER_PATH"])
    return webdriver.Chrome(options=options, service=service)


async def scrape(item: Item, driver: webdriver.Chrome) -> bool:
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
        name = driver.find_element("xpath", "/html/body/div[1]/div/main/div/div[1]/div/div[2]/div[2]/h1/span").text
        _price = driver.find_element("xpath", "/html/body/div[1]/div/main/div/div[1]/div/div[2]/div[3]/div/span").text

        _price = _price.replace("Price\n", "")
        price, currency = split_currency_string(_price)

        record = Record(name=name, url=item.url, price=price, currency=currency)

        await record.create()

        if item.name is None:
            item.name = name
            await item.save()

        return True
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


async def run_scraper(driver: webdriver.Chrome):
    items = await db.database.get_items()
    for item in items:
        await scrape(item, driver)
