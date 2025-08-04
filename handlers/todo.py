from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.todo_manager import TodoManager
from datetime import datetime, timedelta

router = Router()
todo_manager = TodoManager()
router.todo_state = {}
router.todo_temp = {}

def get_todo_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати завдання")],
            [KeyboardButton(text="📋 Переглянути завдання")],
            [KeyboardButton(text="✅ Позначити як виконане")],
            [KeyboardButton(text="❌ Видалити завдання")],
            [KeyboardButton(text="🔙 Назад до меню")]
        ],
        resize_keyboard=True
    )

def get_date_keyboard():
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=str(today))],
            [KeyboardButton(text=str(tomorrow))],
            [KeyboardButton(text="📅 Ввести свою дату (РРРР-ММ-ДД)")]
        ],
        resize_keyboard=True
    )

async def show_todo_menu(message: types.Message):
    await message.answer("📝 Меню завдань:", reply_markup=get_todo_menu())

@router.message(F.text.in_([
    "➕ Додати завдання",
    "📋 Переглянути завдання",
    "❌ Видалити завдання",
    "✅ Позначити як виконане",
    "🔙 Назад до меню"
]))
async def handle_todo_menu(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if text == "➕ Додати завдання":
        await message.answer("✏️ Введи текст нового завдання:")
        router.todo_state[user_id] = "awaiting_task"

    elif text == "📋 Переглянути завдання":
        dates = todo_manager.get_dates(user_id)
        if not dates:
            await message.answer("✅ У тебе поки немає завдань.")
            return await show_todo_menu(message)
        date_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=d)] for d in dates], resize_keyboard=True)
        await message.answer("📅 Обери дату:", reply_markup=date_keyboard)
        router.todo_state[user_id] = "choosing_day"

    elif text == "❌ Видалити завдання":
        dates = todo_manager.get_dates(user_id)
        if not dates:
            await message.answer("✅ У тебе поки немає завдань.")
            return await show_todo_menu(message)
        date_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=d)] for d in dates], resize_keyboard=True)
        await message.answer("📅 Обери дату списку для видалення завдання:", reply_markup=date_keyboard)
        router.todo_state[user_id] = "awaiting_delete_date"

    elif text == "✅ Позначити як виконане":
        dates = todo_manager.get_dates(user_id)
        if not dates:
            await message.answer("✅ У тебе поки немає завдань.")
            return await show_todo_menu(message)
        date_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=d)] for d in dates], resize_keyboard=True)
        await message.answer("📅 Обери дату списку для позначення завдання:", reply_markup=date_keyboard)
        router.todo_state[user_id] = "awaiting_done_date"

    elif text == "🔙 Назад до меню":
        from handlers.main_menu import send_welcome
        await send_welcome(message)

@router.message(F.text)
async def handle_task_steps(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = router.todo_state.get(user_id)

    if state == "awaiting_task":
        router.todo_temp[user_id] = {"task": text}
        await message.answer("📅 Обери дату для завдання:", reply_markup=get_date_keyboard())
        router.todo_state[user_id] = "awaiting_date"

    elif state == "awaiting_date":
        if text.lower().startswith("📅"):
            await message.answer("✏️ Введи дату у форматі РРРР-ММ-ДД:")
            return
        try:
            date = str(datetime.strptime(text, "%Y-%m-%d").date())
        except Exception:
            return await message.answer("⚠️ Некоректна дата. Спробуй ще раз.")
        task = router.todo_temp[user_id].get("task")
        todo_manager.add_task(user_id, task, date)
        await message.answer("✅ Завдання додано.")
        router.todo_state[user_id] = None
        router.todo_temp[user_id] = None
        await show_todo_menu(message)

    elif state == "choosing_day":
        tasks = todo_manager.get_tasks(user_id, text)
        if tasks:
            task_list = "\n".join(f"{i+1}. {'✅' if t[1] else '🕓'} {t[0]}" for i, t in enumerate(tasks))
            await message.answer(f"📋 Завдання на {text}:\n{task_list}")
        else:
            await message.answer("❌ Завдань на цю дату немає.")
        router.todo_state[user_id] = None
        await show_todo_menu(message)

    elif state == "awaiting_delete_date":
        router.todo_temp[user_id] = {"date": text}
        tasks = todo_manager.get_tasks(user_id, text)
        if tasks:
            task_list = "\n".join(f"{i+1}. {'✅' if t[1] else '🕓'} {t[0]}" for i, t in enumerate(tasks))
            await message.answer(f"🗑 Обери завдання для видалення:\n{task_list}\n✏️ Введи номер завдання:")
            router.todo_state[user_id] = "awaiting_delete_index"
        else:
            await message.answer("❌ Завдань на цю дату немає.")
            router.todo_state[user_id] = None
            await show_todo_menu(message)

    elif state == "awaiting_delete_index":
        try:
            index = int(text) - 1
            date = router.todo_temp[user_id].get("date")
            todo_manager.delete_task(user_id, date, index)
            await message.answer("🗑 Завдання видалено.")
        except:
            await message.answer("⚠️ Введи коректний номер.")
        router.todo_state[user_id] = None
        router.todo_temp[user_id] = None
        await show_todo_menu(message)

    elif state == "awaiting_done_date":
        router.todo_temp[user_id] = {"date": text}
        tasks = todo_manager.get_tasks(user_id, text)
        if tasks:
            task_list = "\n".join(f"{i+1}. {'✅' if t[1] else '🕓'} {t[0]}" for i, t in enumerate(tasks))
            await message.answer(f"☑️ Обери завдання для позначення як виконане:\n{task_list}\n✏️ Введи номер завдання:")
            router.todo_state[user_id] = "awaiting_done_index"
        else:
            await message.answer("❌ Завдань на цю дату немає.")
            router.todo_state[user_id] = None
            await show_todo_menu(message)

    elif state == "awaiting_done_index":
        try:
            index = int(text) - 1
            date = router.todo_temp[user_id].get("date")
            todo_manager.mark_done(user_id, date, index)
            await message.answer("✅ Завдання позначено як виконане.")
        except:
            await message.answer("⚠️ Введи коректний номер.")
        router.todo_state[user_id] = None
        router.todo_temp[user_id] = None
        await show_todo_menu(message)