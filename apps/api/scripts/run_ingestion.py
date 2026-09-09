import asyncio

from app.core.logger import setup_logging
from app.db.db import SessionLocal
from workers.ingestion.worker import IngestionWorker


async def main() -> None:
    setup_logging()
    async with SessionLocal() as session:
        results = await IngestionWorker(session).run()
        print("\nWorker 2 result:")
        for result in results:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())