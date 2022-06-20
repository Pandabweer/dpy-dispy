import asyncio

from client import Dispy
from constants import config

client = Dispy()


async def main() -> None:
    async with client:
        await client.start(config.bot.token)

if __name__ == "__main__":
    asyncio.run(main())
