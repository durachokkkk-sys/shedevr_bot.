import os
import asyncio
from flask import Flask
from bot import dp, bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# Запускаем бота в отдельной асинхронной задаче
async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем бота в фоновом режиме
    asyncio.create_task(run_bot())  # Исправлено: запуск через create_task
    # Запускаем веб-сервер
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
