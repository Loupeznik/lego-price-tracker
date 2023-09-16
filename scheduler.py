import asyncio
import os
from dotenv import load_dotenv

import db.database
import scraper

from infra import sentry


async def main():
    load_dotenv()
    
    sentry.add_sentry(bool(os.environ["SENTRY_ENABLED"]), os.environ["SENTRY_DSN"])

    await db.database.init()
    await scraper.run_scraper(scraper.get_driver())


if __name__ == "__main__":
    asyncio.run(main())
