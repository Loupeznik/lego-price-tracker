from dotenv import load_dotenv
from fastapi import FastAPI
from starlette import status
from starlette.responses import Response

import db.database
import scraper
from db.item import Item

app = FastAPI(
    title='Lego Price Tracker API',
    description='REST API for tracking Lego prices',
    version='1.0.0',
    license_info={
        'name': 'MIT',
        'url': 'https://github.com/Loupeznik/lego-price-tracker/blob/master/LICENSE'
    }
)


@app.get("/items")
async def get_items():
    data = await db.database.get_items()

    return data


@app.post("/items")
async def add_item(item: Item):
    await db.database.add_item(item)

    return Response(status_code=status.HTTP_201_CREATED)


@app.delete("/items/{id}")
async def delete_item(item_id: str):
    result = await db.database.delete_item(item_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT if result else status.HTTP_404_NOT_FOUND)


@app.get("/records/{url}")
async def get_records(url: str = None):
    if url is None:
        data = await db.database.get_records()
    else:
        data = await db.database.get_record_by_url(url)
        if data is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    return data


@app.get("/scrape")
async def scrape():
    driver = scraper.get_driver()
    items = await db.database.get_items()
    for item in items:
        await scraper.scrape(item, driver)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.on_event("startup")
async def start():
    load_dotenv()

    await db.database.init()
