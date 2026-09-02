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
async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем бота в фоновом режиме через asyncio.run()
    asyncio.run(start_bot())  # <--- ИСПРАВЛЕНО: используем asyncio.run
    
    # Запускаем веб-сервер
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
