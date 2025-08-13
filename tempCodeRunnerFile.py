import os
import json
import asyncio
import logging
import aiocron
from datetime import datetime, timedelta



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

BIRTHDAYS_DATA = "birthdays.json"

def load_birthdays():
    if os.path.exists(BIRTHDAYS_DATA) and os.path.getsize(BIRTHDAYS_DATA) > 0:
        with open(BIRTHDAYS_DATA, "r") as f:
            return json.load(f)
    else:
        return {"users": []}

    
def save_birthdays(data):
    with open(BIRTHDAYS_DATA, "w") as f:
        json.dump(data, f, indent=4)

@aiocron.crontab("0 0 * * *")
async def daily_birthday_check():
    from app.handlers import check_birthdays
    print("Запуск шедулера")
    await check_birthdays()
    print("Запущен шедулер")


async def main():
    from app.handlers import router
    
    dp.include_router(router)

    logger.info("Starting bot...")
    
    daily_birthday_check()
    # loop = asyncio.get_event_loop()
    # loop.create_task(check_birthdays())
    
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот отключен")
