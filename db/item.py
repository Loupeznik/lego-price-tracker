from typing import Optional

import pymongo
from beanie import Document, Indexed


class Item(Document):
    url: Indexed(str, unique=True)
    name: Optional[str]

    class Settings:
        name = "items"
        indexes = [
            [
                ("url", pymongo.TEXT),
                ("name", pymongo.TEXT),
            ],
        ]
