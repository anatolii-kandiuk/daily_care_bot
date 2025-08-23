import asyncio
from datetime import datetime, timedelta
from services.todo_manager import TodoManager
from services.weather_api import fetch_weather_today
from services.user_settings import get_user_city

todo_manager = TodoManager()

class Scheduler:
    def __init__(self, bot):
        self.bot = bot
        self.task = None
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            now = datetime.now()
            next_run = self._next_run_time(now)
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self.send_reminders(next_run)

    def _next_run_time(self, now):
        today_6 = now.replace(hour=6, minute=0, second=0, microsecond=0)
        today_12 = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now < today_6:
            return today_6
        elif now < today_12:
            return today_12
        else:
            return (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

    async def send_reminders(self, run_time):
        users = todo_manager.get_all_users_with_tasks(run_time.date())

        for user_id in users:
            tasks = todo_manager.get_tasks(user_id, str(run_time.date()))
            if not tasks:
                continue

            greeting = "🌅 *Добрий ранок!*" if run_time.hour == 6 else "☀️ *Добрий день!*"
            message = f"{greeting}\n\n📝 *Твої завдання на сьогодні:*"

            for i, t in enumerate(tasks, start=1):
                status = "✅" if t[1] else "🕓"
                message += f"\n{i}. {status} {t[0]}"

            try:
                city = get_user_city(user_id)
                weather = fetch_weather_today(city)
                temp = round(weather["main"]["temp"])
                feels_like = round(weather["main"]["feels_like"])
                desc = weather["weather"][0]["description"].capitalize()
                wind_speed = weather["wind"]["speed"]

                message += (
                    f"\n\n🌦 *Погода у {city}:*\n"
                    f"• {desc}\n"
                    f"• 🌡 Температура: {temp}°C (відчувається як {feels_like}°C)\n"
                    f"• 💨 Вітер: {wind_speed} м/с"
                )
            except Exception as e:
                message += "\n\n⚠️ Не вдалося отримати прогноз погоди."
            try:
                await self.bot.send_message(user_id, message, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send reminder to {user_id}: {e}")
