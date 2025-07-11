import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


from projectnum1.db import save_to_db, save_rating


user_router = Router()


class DosugStates(StatesGroup):
    mood = State()
    free_time = State()
    people = State()


@user_router.message(Command("start_dosug"))
async def start_dosug(message: Message, state: FSMContext):
    mood_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Веселоe")],
        [KeyboardButton(text="Грустноe")],
        [KeyboardButton(text="Спокойноe")]
    ], resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Привет! Как у тебя настроение?", reply_markup=mood_kb)
    await state.set_state(DosugStates.mood)


@user_router.message(DosugStates.mood)
async def get_mood(message: Message, state: FSMContext):
    await state.update_data(mood=message.text.lower())
    await message.answer("Сколько у тебя свободного времени (в часах)?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DosugStates.free_time)


@user_router.message(DosugStates.free_time)
async def get_time(message: Message, state: FSMContext):
    try:
        hours = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, укажи время в часах (например, 1.5 или 2).")
        return

    await state.update_data(free_time=hours)
    await message.answer("Сколько человек участвуют в досуге?")
    await state.set_state(DosugStates.people)


@user_router.message(DosugStates.people)
async def get_people(message: Message, state: FSMContext):
    try:
        people = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введи целое число.")
        return

    await state.update_data(people=people)
    data = await state.get_data()

    mood = data.get("mood")
    free_time = float(data.get("free_time"))
    user_id = message.from_user.id


    save_to_db(user_id, mood, free_time, people)

    suggestion = suggest_activity(mood, free_time, people)

    await state.update_data(suggestion=suggestion)

    rate_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Да", callback_data="rate_yes")],
        [InlineKeyboardButton(text="👎 Нет", callback_data="rate_no")]
    ])

    await message.answer(f"🧠 Вот идея для досуга:\n👉 {suggestion}\n\n Хочешь занести идею в таблицу избранное ?", reply_markup=rate_kb)



def suggest_activity(mood, time, people):
    mood = mood.lower()
    suggestions = []

    if "груст" in mood:
        if people == 1:
            if time < 1:
                suggestions = [
                    "🎧 Послушай расслабляющую музыку",
                    "🧘 Сделай дыхательную гимнастику",
                    "📱 Посмотри короткое мотивационное видео"
                ]
            elif time < 2:
                suggestions = [
                    "🎬 Посмотри добрый фильм",
                    "🚶‍♂️ Сходи на прогулку",
                    "🎨 Нарисуй свои эмоции"
                ]
            else:
                suggestions = [
                    "🛁 Устрой себе SPA-день",
                    "📓 Запиши мысли в дневник",
                    "🎥 Посмотри вдохновляющий фильм"
                ]
        else:
            suggestions = [
                "🧩 Настолки с друзьями и чай — уютно и весело",
                "🎞 Совместный просмотр комедии",
                "🐊 Игра в 'Крокодила' — зарядит энергией"
            ]

    elif "весел" in mood:
        if people == 1:
            suggestions = [
                "💃 Потанцуй под любимую музыку",
                "🤣 Посмотри стендап или мемы",
                "🎮 Поиграй в весёлую игру"
            ]
        else:
            if time >= 2:
                suggestions = [
                    "🎳 Сходите в боулинг или в парк",
                    "🧺 Устройте пикник",
                    "📹 Снимите весёлое видео вместе"
                ]
            else:
                suggestions = [
                    "🎲 Игра в 'Uno' или 'Крокодила'",
                    "🎵 Музыкальная угадайка",
                    "🎤 Караоке-домашка"
                ]

    elif "спокойн" in mood:
        if people == 1:
            suggestions = [
                "📚 Чтение книги с чаем",
                "🎧 Медитация и музыка",
                "🌳 Прогулка в одиночестве"
            ]
        else:
            suggestions = [
                "🎬 Совместный просмотр фильма",
                "♟ Игра в шахматы или стратегии",
                "☕️ Обсуждение книг или жизни за чаем"
            ]
    else:
        suggestions = [
            "🚀 Попробуй что-то новое — может это будет твоё!",
            "🔁 Сделай перерыв и перезагрузись",
            "🎯 Делай то, что приносит тебе радость"
        ]

    return random.choice(suggestions)

@user_router.callback_query(F.data == "rate_yes")
async def on_rate_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    suggestion = data.get("suggestion")

    rating_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="rating_1"),
         InlineKeyboardButton(text="2", callback_data="rating_2"),
         InlineKeyboardButton(text="3", callback_data="rating_3"),
         InlineKeyboardButton(text="4", callback_data="rating_4"),
         InlineKeyboardButton(text="5", callback_data="rating_5")]
    ])

    await callback.message.edit_text(
        f"🧠 Вот идея для досуга:\n👉 {suggestion}\n\nОцени от 1 до 5:",
        reply_markup=rating_kb
    )

    await callback.answer()

@user_router.callback_query(F.data.startswith("rating_"))
async def on_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    data = await state.get_data()
    suggestion = data.get("suggestion")
    user_id = callback.from_user.id

    save_rating(user_id, suggestion, rating)

    await callback.message.edit_text(f"Спасибо! Ваша оценка: {rating} ⭐")
    await callback.answer()
    await state.clear()


@user_router.callback_query(F.data == "rate_no")
async def on_rate_no(callback: CallbackQuery):
    await callback.message.edit_text("Как пожелаете 🙌")
    await callback.answer()





