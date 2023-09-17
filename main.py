import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette import status
from starlette.responses import Response

import db.database
import scraper
from db.item import Item
from db.record import Record

from infra import sentry

app = FastAPI(
    title='Lego Price Tracker API',
    description='REST API for tracking Lego prices',
    version='1.0.0',
    license_info={
        'name': 'MIT',
        'url': 'https://github.com/Loupeznik/lego-price-tracker/blob/master/LICENSE',
    },

)


@app.get("/items", tags=["items"])
async def get_items() -> list[Item]:
    data = await db.database.get_items()

    return data


@app.post("/items", status_code=status.HTTP_201_CREATED, tags=["items"], responses={201: {"description": "Item created"}})
async def add_item(item: Item):
    await db.database.add_item(item)

    return Response(status_code=status.HTTP_201_CREATED)


@app.delete("/items/{id}", tags=["items"], status_code=status.HTTP_204_NO_CONTENT,
            responses={204: {"description": "Item deleted"}, 404: {"description": "Item not found"}})
async def delete_item(item_id: str):
    result = await db.database.delete_item(item_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT if result else status.HTTP_404_NOT_FOUND)


@app.get("/records/{set_id}", tags=["records"], status_code=status.HTTP_200_OK, responses={404: {"description": "Set not found"}})
async def get_records_by_set_id(set_id: int = None) -> list[Record] or Response:
    data = await db.database.get_records_by_set_id(set_id)
    if data is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return data


@app.get("/records", tags=["records"])
async def get_records() -> list[Record]:
    data = await db.database.get_records()

    return data


@app.get("/scrape", status_code=status.HTTP_204_NO_CONTENT, tags=["scrape"])
async def scrape():
    driver = scraper.get_driver()
    items = await db.database.get_items()
    for item in items:
        await scraper.scrape(item, driver)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.on_event("startup")
async def start():
    load_dotenv()

    sentry.add_sentry(
        bool(os.environ["SENTRY_ENABLED"]), os.environ["SENTRY_DSN"])
    await db.database.init()
