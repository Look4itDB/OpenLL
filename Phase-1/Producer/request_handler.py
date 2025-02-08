import sys
sys.dont_write_bytecode = True

import aiohttp
import random
from config import API_URL, DEVICE_IDS

async def send_request(session, index):
    data = {
        "device_id": random.choice(DEVICE_IDS),
        "coordinates": [[index * 0.001, index * 0.002]]
    }
    async with session.post(API_URL, json=data) as response:
        status = response.status
        text = await response.text()
        return f"Request {index} -> Status: {status}, Response: {text}"
