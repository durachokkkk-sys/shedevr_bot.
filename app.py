import os
import threading
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

async def start_bot():
    await dp.start_polling(bot)

# Запускаем бота в отдельном потоке
def run_bot_thread():
    asyncio.run(start_bot())

if __name__ == "__main__":
    # Поток для бота
    bot_thread = threading.Thread(target=run_bot_thread)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Веб-сервер (это то, что Render ищет)
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
