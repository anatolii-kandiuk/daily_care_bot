import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from handlers import main_menu, todo, weather, gpt_assistant
from utils.scheduler import Scheduler
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(
    main_menu.router,
    weather.router,
    todo.router,
    gpt_assistant.router,
)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущено.")
    
    scheduler = Scheduler(bot)
    asyncio.create_task(scheduler.start())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
