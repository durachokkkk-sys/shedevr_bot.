import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

from config import (
    BOT_TOKEN, DATE_1, DATE_2, TOPIC_1, TOPIC_2, PRICE, ADDRESS, PHONE,
    EVENT_DATETIME_1, EVENT_DATETIME_2,
    MSG_START, MSG_REST, MSG_FRIENDS, MSG_NEWBIE, MSG_SCHEDULE, MSG_CONFIRM,
    MSG_NO_EXPERIENCE, MSG_REMINDER, MSG_REMINDER_24H,
    MSG_MY_BOOKING, MSG_CANCEL_SUCCESS, MSG_CANCEL_TOO_LATE, MSG_NO_BOOKING,
    MSG_ALREADY_BOOKED, MSG_PLAIN_TEXT
)
from database import (
    add_booking, get_all_bookings, get_booking_by_user, delete_booking,
    get_users_to_remind_24h, get_users_to_remind_3h, mark_reminded_24h, mark_reminded_3h
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КНОПКИ ---
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋 Хочу отдохнуть от работы", callback_data="rest")],
        [InlineKeyboardButton(text="👯‍♀️ Хочу встретиться с подругами", callback_data="friends")],
        [InlineKeyboardButton(text="✨ Хочу попробовать что-то новое", callback_data="newbie")],
        [InlineKeyboardButton(text="📋 Моя запись", callback_data="my_booking")]
    ])

def get_rest_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Смотреть расписание вечеров", callback_data="schedule")],
        [InlineKeyboardButton(text="🖌 Я никогда не рисовала", callback_data="no_exp")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def get_schedule_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎨 Записаться на {DATE_1} ({TOPIC_1})", callback_data="book_1")],
        [InlineKeyboardButton(text=f"🎨 Записаться на {DATE_2} ({TOPIC_2})", callback_data="book_2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def get_my_booking_menu(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"cancel_{booking_id}")],
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_main")]
    ])

# --- АДМИН ---
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id == 123456789:
        bookings = get_all_bookings()
        if bookings:
            text = "📋 **Список записавшихся:**\n\n"
            for booking in bookings:
                text += f"👤 {booking[0]} (@{booking[1]})\n📅 {booking[2]} — {booking[3]}\n🕒 {booking[4]}\n\n"
            await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("Пока нет записей.")
    else:
        await message.answer("⛔ У вас нет доступа к этой команде.")

# --- НАПОМИНАНИЯ ---
async def send_reminders():
    while True:
        try:
            now = datetime.now()
            
            for booking in get_users_to_remind_24h():
                user_id, first_name, event_datetime_str, booking_id = booking
                event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
                delta = event_datetime - now
                if 0 < delta.total_seconds() <= 24 * 3600:
                    try:
                        await bot.send_message(user_id, MSG_REMINDER_24H, parse_mode="Markdown")
                        mark_reminded_24h(booking_id)
                    except Exception:
                        mark_reminded_24h(booking_id)

            for booking in get_users_to_remind_3h():
                user_id, first_name, event_datetime_str, booking_id = booking
                event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
                delta = event_datetime - now
                if 0 < delta.total_seconds() <= 3 * 3600:
                    try:
                        await bot.send_message(user_id, MSG_REMINDER, parse_mode="Markdown")
                        mark_reminded_3h(booking_id)
                    except Exception:
                        mark_reminded_3h(booking_id)

            await asyncio.sleep(60)
        except Exception as e:
            print(f"Ошибка в напоминаниях: {e}")
            await asyncio.sleep(60)

# --- ОБРАБОТЧИКИ ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(MSG_START, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "rest")
async def process_rest(callback: CallbackQuery):
    await callback.message.edit_text(MSG_REST, reply_markup=get_rest_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "friends")
async def process_friends(callback: CallbackQuery):
    await callback.message.edit_text(MSG_FRIENDS, reply_markup=get_rest_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "newbie")
async def process_newbie(callback: CallbackQuery):
    await callback.message.edit_text(MSG_NEWBIE, reply_markup=get_rest_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "no_exp")
async def process_no_exp(callback: CallbackQuery):
    await callback.message.edit_text(MSG_NO_EXPERIENCE, reply_markup=get_rest_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_main")
async def process_back_main(callback: CallbackQuery):
    await callback.message.edit_text(MSG_START, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "schedule")
async def process_schedule(callback: CallbackQuery):
    await callback.message.answer(MSG_SCHEDULE, reply_markup=get_schedule_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "book_1")
async def process_book_1(callback: CallbackQuery):
    user = callback.from_user
    existing_booking = get_booking_by_user(user.id)
    if existing_booking:
        await callback.answer(MSG_ALREADY_BOOKED, show_alert=True)
        return
    add_booking(user.id, user.username or "нет_username", user.first_name or "Гость", DATE_1, TOPIC_1, EVENT_DATETIME_1)
    await callback.message.edit_text(
        f"Поздравляем! Вы забронировали место на вечер **{DATE_1} ({TOPIC_1})** 🎉\n\n{MSG_CONFIRM}",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "book_2")
async def process_book_2(callback: CallbackQuery):
    user = callback.from_user
    existing_booking = get_booking_by_user(user.id)
    if existing_booking:
        await callback.answer(MSG_ALREADY_BOOKED, show_alert=True)
        return
    add_booking(user.id, user.username or "нет_username", user.first_name or "Гость", DATE_2, TOPIC_2, EVENT_DATETIME_2)
    await callback.message.edit_text(
        f"Поздравляем! Вы забронировали место на вечер **{DATE_2} ({TOPIC_2})** 🎉\n\n{MSG_CONFIRM}",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "my_booking")
async def process_my_booking(callback: CallbackQuery):
    user_id = callback.from_user.id
    booking = get_booking_by_user(user_id)
    if booking:
        booking_id, date, topic, event_datetime = booking
        text = MSG_MY_BOOKING.format(topic=topic, date=date)
        await callback.message.edit_text(
            text,
            reply_markup=get_my_booking_menu(booking_id),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(MSG_NO_BOOKING, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("cancel_"))
async def process_cancel(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    booking = get_booking_by_user(user_id)
    if not booking:
        await callback.message.edit_text(MSG_NO_BOOKING, parse_mode="Markdown")
        return
    
    booking_id_in_db, date, topic, event_datetime_str = booking
    event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
    now = datetime.now()
    delta = event_datetime - now
    
    if delta.total_seconds() > 12 * 3600:
        delete_booking(booking_id_in_db)
        await callback.message.edit_text(MSG_CANCEL_SUCCESS, parse_mode="Markdown")
    else:
        await callback.message.edit_text(MSG_CANCEL_TOO_LATE, parse_mode="Markdown")

# --- ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ---
@dp.message(F.text)
async def process_text(message: Message):
    await message.answer(MSG_PLAIN_TEXT, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- ЗАПУСК ---
async def main():
    print("Бот запущен и готов к работе!")
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
