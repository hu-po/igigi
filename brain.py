import asyncio
import os
import sys

from .utils import scrape_callback, send_file
from .hparams import HPARAMS

async def main_loop(hparams: dict = HPARAMS):

    # scrape for image + image log

    # scrape for servo + servo log

    results = await asyncio.gather(*_tasks, return_exceptions=True)

    # ask VLM for commands

    results = await asyncio.gather(*_tasks, return_exceptions=True)
    
    # write commands, send commands

    results = await asyncio.gather(*_tasks, return_exceptions=True)

async def test(hparams: dict = HPARAMS):
    pass


if __name__ == "__main__":
    asyncio.run(test())
    asyncio.run(main_loop())
