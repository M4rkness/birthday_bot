import asyncio
from main import main

def keep_alive():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

application = keep_alive

