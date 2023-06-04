import asyncio
from dotenv import load_dotenv

import db.database
import scraper


async def main():
    load_dotenv()
    await db.database.init()
    await scraper.run_scraper(scraper.get_driver())


if __name__ == "__main__":
    asyncio.run(main())
