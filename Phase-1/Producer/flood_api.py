import asyncio
import aiohttp
from request_handler import send_request

async def flood_api(request_count=100000):
    """Send multiple concurrent requests to the API"""
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(request_count)]
        results = await asyncio.gather(*tasks)
        for res in results:
            print(res)
