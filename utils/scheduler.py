import asyncio
from datetime import datetime, time, timedelta
from aiogram import Bot
from services.todo_manager import TodoManager

todo_manager = TodoManager()

class Scheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.task = None
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            now = datetime.now()
            # Розрахунок часу до наступного пуску - 06:00 або 12:00
            next_run = self._next_run_time(now)
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self.send_reminders(next_run.date())
    
    def _next_run_time(self, now: datetime) -> datetime:
        today_6 = now.replace(hour=6, minute=0, second=0, microsecond=0)
        today_12 = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now < today_6:
            return today_6
        elif now < today_12:
            return today_12
        else:
            # Наступний день 6:00 ранку
            return (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

    async def send_reminders(self, date):
        users = todo_manager.get_all_users_with_tasks(date)
        for user_id in users:
            tasks = todo_manager.get_tasks(user_id, str(date))
            if not tasks:
                continue
            tasks_text = "\n".join(f"{i+1}. {'✅' if t[1] else '🕓'} {t[0]}" for i, t in enumerate(tasks))
            if date.hour == 6:
                greeting = "Добрий ранок! Ось твої завдання на сьогодні:\n"
            else:
                greeting = "Південь! Не забудь про свої завдання:\n"
            message = f"{greeting}{tasks_text}\n\nПОГОДА"
            try:
                await self.bot.send_message(user_id, message)
            except Exception as e:
                print(f"Failed to send reminder to {user_id}: {e}")
