import asyncio

from app.scheduler.scheduler import create_scheduler


async def main():
    scheduler = create_scheduler()
    scheduler.start()

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())