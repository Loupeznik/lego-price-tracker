from datetime import datetime

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class Record(Document):
    name: Indexed(str)
    url: Indexed(str)
    price: float
    currency: str
    date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "records"
        indexes = [
            [
                ("url", pymongo.TEXT),
                ("name", pymongo.TEXT),
            ],
        ]
