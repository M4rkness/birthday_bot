import asyncio
import logging
from datetime import datetime, timedelta

from keep_alive import keep_alive

keep_alive()

from dotenv import load_dotenv

from app.config import dp, bot

load_dotenv()

logging.basicConfig(level=logging.INFO)



logging.basicConfig(level=logging.DEBUG, filename='my_logging.log', format='%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]', datefmt='%d/%m/%Y %I:%M:%S',
                    encoding = 'utf-8', filemode='w')

logger = logging.getLogger(__name__)
handler = logging.FileHandler('test.log', encoding='utf-8')
formatter = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]')
handler.setFormatter(formatter)
logger.addHandler(handler)





async def main():
    from app.handlers import router
    
    dp.include_router(router)

    logger.info("Starting bot...")
    
    # loop = asyncio.get_event_loop()
    # loop.create_task(check_birthdays())
    
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот отключен")
