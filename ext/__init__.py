import os
import asyncio

__title__ = "Dispy"
__author__ = "Pandabweer"
__license__ = "MIT"
__version__ = "0.0.1"

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
