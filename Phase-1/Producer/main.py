import sys
sys.dont_write_bytecode = True

import asyncio
from flood_api import flood_api

if __name__ == "__main__":
    asyncio.run(flood_api(request_count=300000, concurrency=2000))
