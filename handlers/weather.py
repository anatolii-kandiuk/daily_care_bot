from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.weather_api import fetch_weather_today, fetch_weather_forecast
from datetime import datetime, timedelta
from handlers.main_menu import send_welcome

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

router = Router()
router.weather_state = {}
router.user_city = {}

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

def format_today_with_avg(current_data, forecast_data):
    if current_data.get("cod") != 200:
        return "❌ Місто не знайдено."

    today_date = datetime.now().date()
    today_list = [f for f in forecast_data["list"] if datetime.fromtimestamp(f["dt"]).date() == today_date]

    avg_temp = round(sum(f["main"]["temp"] for f in today_list) / len(today_list), 1) if today_list else None

    city = current_data["name"]
    temp = current_data["main"]["temp"]
    feels = current_data["main"]["feels_like"]
    desc = current_data["weather"][0]["description"].capitalize()
    wind = current_data["wind"]["speed"]
    emoji = get_weather_emoji(current_data["weather"][0]["main"])

    avg_line = f"\n📊 Середнє за день: {avg_temp}°C" if avg_temp is not None else ""

    return (
        f"{emoji} *{city}*\n"
        f"🕒 Поточна температура: {temp}°C (відчувається як {feels}°C)\n"
        f"💨 Вітер: {wind} м/с\n"
        f"📋 {desc}"
        f"{avg_line}"
    )

def format_forecast_with_avg(forecast_data, day_offset=1):
    if forecast_data.get("cod") != "200":
        return "❌ Місто не знайдено."

    target_date = (datetime.now() + timedelta(days=day_offset)).date()
    day_data = [f for f in forecast_data["list"] if datetime.fromtimestamp(f["dt"]).date() == target_date]

    if not day_data:
        return "❌ Немає даних прогнозу."

    avg_temp = round(sum(f["main"]["temp"] for f in day_data) / len(day_data), 1)
    current_hour_data = day_data[0]
    desc = current_hour_data["weather"][0]["description"].capitalize()
    emoji = get_weather_emoji(current_hour_data["weather"][0]["main"])
    temp_now = current_hour_data["main"]["temp"]

    return (
        f"{emoji} *Прогноз на {target_date}*\n"
        f"🕒 Приблизно зараз: {temp_now}°C\n"
        f"📊 Середня температура: {avg_temp}°C\n"
        f"📋 {desc}"
    )

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
        current = fetch_weather_today(city)
        forecast = fetch_weather_forecast(city)
        await message.answer(format_today_with_avg(current, forecast), parse_mode="Markdown")

    elif text == "🌅 Погода на завтра":
        forecast = fetch_weather_forecast(city)
        await message.answer(format_forecast_with_avg(forecast, day_offset=1), parse_mode="Markdown")

    elif text == "📆 Прогноз на тиждень":
        data = fetch_weather_forecast(city)
        reply = []
        for i in range(1, 6):
            reply.append(format_forecast_with_avg(data, day_offset=i))
        await message.answer("\n\n".join(reply), parse_mode="Markdown")

    elif text == "🌍 Змінити місто":
        await message.answer("Введіть нове місто:")
        router.weather_state[user_id] = "awaiting_city"

    elif text == "🔙 Назад":
        await send_welcome(message)

@router.message()
async def handle_city_input(message: types.Message):
    user_id = message.from_user.id
    if router.weather_state.get(user_id) == "awaiting_city":
        city = message.text.strip()
        router.user_city[user_id] = city
        router.weather_state.pop(user_id, None)
        await message.answer(f"✅ Місто змінено на: *{city}*", parse_mode="Markdown")
