from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Кнопки головного меню
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Плани", callback_data="menu_plans")],
        [InlineKeyboardButton(text="🌤 Погода", callback_data="menu_weather")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="menu_settings")]
    ])
    return keyboard

# Підменю "Плани"
def get_plans_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Поточний план", callback_data="plans_show")],
        [InlineKeyboardButton(text="➕ Додати пункт", callback_data="plans_add")],
        [InlineKeyboardButton(text="📅 План на завтра", callback_data="plans_tomorrow")],
        [InlineKeyboardButton(text="✏️ Редагувати", callback_data="plans_edit")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back_main")]
    ])
    return keyboard

# Підменю "Погода"
def get_weather_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Поточна погода", callback_data="weather_current")],
        [InlineKeyboardButton(text="🌍 Змінити регіон", callback_data="weather_change")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back_main")]
    ])
    return keyboard

# Підменю "Налаштування"
def get_settings_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Вибір мови", callback_data="settings_language")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back_main")]
    ])
    return keyboard

# Привітання
@router.message(F.text, F.text.lower().in_(["start", "/start", "привіт"]))
async def cmd_start(message: Message):
    await message.answer("👋 Вітаю! Оберіть пункт меню:", reply_markup=get_main_menu())

# Обробники натискань на кнопки
@router.callback_query(F.data == "menu_plans")
async def show_plans_menu(callback: CallbackQuery):
    await callback.message.edit_text("📋 Плани:", reply_markup=get_plans_menu())

@router.callback_query(F.data == "menu_weather")
async def show_weather_menu(callback: CallbackQuery):
    await callback.message.edit_text("🌤 Погода:", reply_markup=get_weather_menu())

@router.callback_query(F.data == "menu_settings")
async def show_settings_menu(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ Налаштування:", reply_markup=get_settings_menu())

# Назад у головне меню
@router.callback_query(F.data == "go_back_main")
async def go_back_main(callback: CallbackQuery):
    await callback.message.edit_text("⬅️ Назад до головного меню:", reply_markup=get_main_menu())
