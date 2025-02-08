import sys
sys.dont_write_bytecode = True

import asyncio
import aiohttp
from request_handler import send_request

async def flood_api(request_count=100000, concurrency=1000):
    # concurrency=2000 means up to 2000 requests in-flight at once
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        async def bound_send_request(i):
            async with semaphore:
                return await send_request(session, i)
        tasks = [bound_send_request(i) for i in range(request_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            print(res)
