from typing import Optional
from datetime import datetime

import pymongo
from beanie import Document, Indexed
from pydantic import Field

class Item(Document):
    url: Indexed(str, unique=True)
    name: Optional[str]
    set_id: Optional[int]
    retiring_soon: Optional[bool]
    retiring_soon_fetch_date: Optional[datetime]
    retired_date: Optional[datetime]

    class Settings:
        name = "items"
        indexes = [
            [
                ("url", pymongo.TEXT),
                ("name", pymongo.TEXT),
            ],
        ]
