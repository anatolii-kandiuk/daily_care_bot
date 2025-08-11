import json
from pathlib import Path
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

LOCALES_DIR = Path(__file__).parent.parent / "locale"
translations = {}

for lang_code in ["uk", "en"]:
    with open(LOCALES_DIR / f"{lang_code}.json", encoding="utf-8") as f:
        translations[lang_code] = json.load(f)

user_languages = {}

def get_user_language(user_id):
    return user_languages.get(user_id, "uk")

def get_translation(user_id):
    lang = get_user_language(user_id)
    return translations.get(lang, translations["uk"])

def get_main_menu(user_id):
    t = get_translation(user_id)["menu"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["todo"])],
            [KeyboardButton(text=t["weather"])],
            [KeyboardButton(text=t["gpt"])],
            [KeyboardButton(text=t["settings"])]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_settings_menu(user_id):
    lang = get_user_language(user_id)
    back_text = "🔙 Назад" if lang == "uk" else "🔙 Back"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇦 Українська"),
                KeyboardButton(text="🇬🇧 English")
            ],
            [KeyboardButton(text=back_text)]
        ],
        resize_keyboard=True
    )
    return keyboard

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    t = get_translation(user_id)
    await message.answer(
        text=t["welcome"],
        reply_markup=get_main_menu(user_id)
    )

@router.message(F.text.in_([
    translations["uk"]["menu"]["todo"],
    translations["uk"]["menu"]["weather"],
    translations["uk"]["menu"]["gpt"],
    translations["uk"]["menu"]["settings"],
    translations["en"]["menu"]["todo"],
    translations["en"]["menu"]["weather"],
    translations["en"]["menu"]["gpt"],
    translations["en"]["menu"]["settings"],
]))
async def handle_menu_selection(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    t = get_translation(user_id)

    if text == t["menu"]["todo"]:
        from handlers.todo import show_todo_menu
        await show_todo_menu(message)
        return
    elif text == t["menu"]["weather"]:
        from handlers.weather import show_weather_menu
        await show_weather_menu(message)
        return
    elif text == t["menu"]["gpt"]:
        await message.answer(t["menu"]["gpt"] + (" обрано" if get_user_language(user_id) == "uk" else " selected"))
        return
    elif text == t["menu"]["settings"]:
        await message.answer(t["settings_menu"]["choose_language"], reply_markup=get_settings_menu(user_id))
        return

@router.message(F.text.in_([
    "🇺🇦 Українська",
    "🇬🇧 English"
]))
async def switch_language(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if text == "🇺🇦 Українська":
        new_lang = "uk"
        language_name = "Українська"
    elif text == "🇬🇧 English":
        new_lang = "en"
        language_name = "English"
    else:
        return

    user_languages[user_id] = new_lang
    t = get_translation(user_id)
    msg = t["language_changed"].format(language=language_name)
    await message.answer(msg, reply_markup=get_main_menu(user_id))
