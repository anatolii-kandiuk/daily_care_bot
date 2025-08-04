import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from handlers import main_menu, todo, weather, gpt_assistant
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
    todo.router,
    weather.router,
    gpt_assistant.router,
)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущено.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
