from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Список завдань")],
            [KeyboardButton(text="☀️ Погода")],
            [KeyboardButton(text="🧠 Консультація GPT")],
            [KeyboardButton(text="* Налаштування")]
        ],
        resize_keyboard=True
    )
    return keyboard

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(
        text="👋 Вітаю! Обери дію з меню нижче:",
        reply_markup=get_main_menu()
    )

@router.message(F.text.in_([
    "📋 Список завдань", "☀️ Погода", "🧠 Консультація GPT", "* Налаштування"
]))
async def handle_menu_selection(message: types.Message):
    text = message.text

    if text == "📋 Список завдань":
        from handlers.todo import show_todo_menu
        await show_todo_menu(message)
    elif text == "☀️ Погода":
        await message.answer("☀️ Обрано: погода")
    elif text == "🧠 Консультація GPT":
        await message.answer("🧠 Обрано: GPT-консультація")
    elif text == "* Налаштування":
        await message.answer("* Обрано: Налаштування")
