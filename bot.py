import os
import requests
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or OPENROUTER_API_KEY")

async def ask_openrouter(question: str) -> str:
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "system", "content": "Ты — мудрый оракул. Отвечай кратко и загадочно."},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.8,
                "max_tokens": 500,
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"OpenRouter error: {e}")
        return "❌ Не могу ответить сейчас."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Привет! Я ИИ-оракул. Задай любой вопрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Думаю...")
    answer = await ask_openrouter(update.message.text)
    await update.message.reply_text(f"🔮 {answer}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()