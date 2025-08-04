from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список завдань", callback_data="menu_todo")
    builder.button(text="☀️ Погода", callback_data="menu_weather")
    builder.button(text="🧠 Консультація GPT", callback_data="menu_gpt")
    builder.button(text="* Налаштування", callback_data="settings")
    builder.adjust(1)

    await message.answer(
        text="👋 Вітаю! Обери дію з меню нижче:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("menu_"))
async def handle_menu_selection(callback: types.CallbackQuery):
    if callback.data == "menu_todo":
        from handlers.todo import show_todo_menu
        await show_todo_menu(callback)
    elif callback.data == "menu_weather":
        await callback.message.answer("☀️ Обрано: погода")
    elif callback.data == "menu_gpt":
        await callback.message.answer("🧠 Обрано: GPT-консультація")
    elif callback.data == "settings":
        await callback.message.answer("* Обрано: Налаштування")
    else:
        await callback.message.answer("❌ Невідомий пункт меню")

    await callback.answer()
