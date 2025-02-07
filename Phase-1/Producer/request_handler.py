import aiohttp
from config import API_URL, DEVICE_ID

async def send_request(session, index):
    """Send a single POST request with random coordinates"""
    data = {
        "device_id": DEVICE_ID,
        "coordinates": [[index * 0.001, index * 0.002]]  # Random small variations
    }
    async with session.post(API_URL, json=data) as response:
        status = response.status
        text = await response.text()
        return f"Request {index} -> Status: {status}, Response: {text}"
