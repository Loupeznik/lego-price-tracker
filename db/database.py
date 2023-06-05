import os

import pymongo
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from db.item import Item
from db.record import Record


async def init():
    client = AsyncIOMotorClient(os.environ["MONGO_CONNECTION_STRING"])
    await init_beanie(database=client.lego, document_models=[Item, Record])


async def get_records():
    return await Record.find_all().to_list()


async def get_items():
    return await Item.find_all().to_list()


async def add_record(record: Record):
    await record.create()


async def add_item(item: Item):
    await item.create()


async def delete_item(item_id: str) -> bool:
    item = await Item.get(item_id)

    if item is None:
        return False

    await item.delete()

    return True


async def get_records_by_set_id(set_id: int) -> list[Record]:
    return await Record.find(Record.set_id == set_id).sort("-date").limit(30).to_list()
