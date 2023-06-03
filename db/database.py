from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from db.item import Item
from db.record import Record


async def init():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.db_name, document_models=[Item, Record])


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


async def get_record_by_url(url: str):
    return await Record.find_one({"url": url})
