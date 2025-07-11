from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import sqlite3


admin = Router()

@admin.message(Command('show_table'))
async def show_table(message: Message):
    conn = sqlite3.connect("dosug.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, mood, free_time, people
        FROM activity_log
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return await message.answer("Таблица `activity_log` пуста.")

    BATCH_SIZE = 10
    for i in range(0, len(rows), BATCH_SIZE):
        chunk = rows[i:i + BATCH_SIZE]
        text = "📄 Данные из таблицы `activity_log`:\n"
        for row in chunk:
            id_, user_id, mood, free_time, people = row
            text += (
                f"\n🆔 Запись #{id_}\n"
                f"👤 User ID: {user_id}\n"
                f"🧠 Настроение: {mood}\n"
                f"⏱ Свободное время: {free_time} ч\n"
                f"👥 Людей: {people}\n"
            )
        await message.answer(text)
