from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()
router.weather_state = {}

def get_weather_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Погода на сьогодні")],
            [KeyboardButton(text="🌅 Погода на завтра")],
            [KeyboardButton(text="📆 Прогноз на тиждень")],
            [KeyboardButton(text="🌍 Змінити місто")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

async def show_weather_menu(message: types.Message):
    await message.answer("🌦 Меню погоди:", reply_markup=get_weather_menu())
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.weather_api import fetch_weather_today, fetch_weather_forecast

router = Router()
router.weather_state = {}
router.user_city = {}  # збереження міст користувачів

def get_weather_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Погода на сьогодні")],
            [KeyboardButton(text="🌅 Погода на завтра")],
            [KeyboardButton(text="📆 Прогноз на тиждень")],
            [KeyboardButton(text="🌍 Змінити місто")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

async def show_weather_menu(message: types.Message):
    await message.answer("🌦 Меню погоди:", reply_markup=get_weather_menu())

def format_today_weather(data):
    if data.get("cod") != 200:
        return "❌ Місто не знайдено."
    city = data["name"]
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    desc = data["weather"][0]["description"].capitalize()
    wind = data["wind"]["speed"]
    emoji = get_weather_emoji(data["weather"][0]["main"])
    return f"{emoji} *{city}*\n🌡 Температура: {temp}°C (відчувається як {feels}°C)\n💨 Вітер: {wind} м/с\n📋 {desc}"

def format_forecast(data, day_offset=1):
    if data.get("cod") != "200":
        return "❌ Місто не знайдено."
    from datetime import datetime, timedelta
    target_date = (datetime.now() + timedelta(days=day_offset)).date()
    day_data = [f for f in data["list"] if datetime.fromtimestamp(f["dt"]).date() == target_date]
    if not day_data:
        return "❌ Немає даних прогнозу."
    avg_temp = round(sum(f["main"]["temp"] for f in day_data) / len(day_data), 1)
    desc = day_data[0]["weather"][0]["description"].capitalize()
    emoji = get_weather_emoji(day_data[0]["weather"][0]["main"])
    return f"{emoji} *Прогноз на {target_date}*\n🌡 Середня температура: {avg_temp}°C\n📋 {desc}"

def get_weather_emoji(condition):
    mapping = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧",
        "Drizzle": "🌦",
        "Thunderstorm": "⛈",
        "Snow": "❄️",
        "Mist": "🌫"
    }
    return mapping.get(condition, "🌍")

@router.message(F.text.in_([
    "📍 Погода на сьогодні",
    "🌅 Погода на завтра",
    "📆 Прогноз на тиждень",
    "🌍 Змінити місто",
    "🔙 Назад"
]))
async def handle_weather_menu(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    city = router.user_city.get(user_id, "Berlin")

    if text == "📍 Погода на сьогодні":
        data = fetch_weather_today(city)
        await message.answer(format_today_weather(data), parse_mode="Markdown")

    elif text == "🌅 Погода на завтра":
        data = fetch_weather_forecast(city)
        await message.answer(format_forecast(data, day_offset=1), parse_mode="Markdown")

    elif text == "📆 Прогноз на тиждень":
        data = fetch_weather_forecast(city)
        from datetime import datetime, timedelta
        reply = []
        for i in range(1, 6):
            reply.append(format_forecast(data, day_offset=i))
        await message.answer("\n\n".join(reply), parse_mode="Markdown")

    elif text == "🌍 Змінити місто":
        await message.answer("Введіть нове місто:")
        router.weather_state[user_id] = "awaiting_city"

    elif text == "🔙 Назад":
        from handlers.main_menu import send_welcome
        await send_welcome(message)

@router.message()
async def handle_city_input(message: types.Message):
    user_id = message.from_user.id
    if router.weather_state.get(user_id) == "awaiting_city":
        city = message.text.strip()
        router.user_city[user_id] = city
        router.weather_state.pop(user_id, None)
        await message.answer(f"✅ Місто змінено на: *{city}*", parse_mode="Markdown")
