import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()
print("TOKEN:", os.getenv("BOT_TOKEN"))
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Мої завдання")],
        [KeyboardButton(text="🌤 Погода")],
        [KeyboardButton(text="⚙ Налаштування")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_handler(message):
    await message.answer("👋 Вітаю! Це DailyCareBot. Оберіть опцію з меню нижче.", reply_markup=main_menu_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
