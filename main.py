import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from openai import OpenAI
import json
import difflib
import sys
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# === Загрузка конфигурации ===
with open("config.json") as f:
    config = json.load(f)

SPREADSHEET_ID = config["spreadsheet_id"]
RANGE_NAME = config["range_name"]
SERVICE_ACCOUNT_FILE = config["google_service_account_file"]
OPENAI_API_KEY = config["openai_api_key"]
TELEGRAM_TOKEN = config["telegram_token"]

# === Подключаем Google Sheets ===
print("🔗 Подключаюсь к Google Sheets...")
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])
df = pd.DataFrame(values[1:], columns=values[0])

print(f"✅ Загружено строк: {len(df)}")

# === Поиск похожих ===
def find_similar(query, top_n=3):
    contents = df["Content"].tolist()
    matches = difflib.get_close_matches(query, contents, n=top_n)
    return df[df["Content"].isin(matches)]

# === GPT ===
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_reply(user_question):
    similar = find_similar(user_question)
    if similar.empty:
        context = "Нет похожих кейсов в базе."
    else:
        context = "\n\n".join(
            f"Q: {row['Content']}\nA: {row['Agent']}" for _, row in similar.iterrows()
        )
    prompt = f"""
Ты — опытный и вежливый агент поддержки.
Используй похожие кейсы ниже, чтобы ответить игроку.

{context}

Вопрос игрока:
{user_question}

Ответь кратко и понятно.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты профессиональный агент поддержки."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# === Telegram bot ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот поддержки Game of Khans. Спроси меня о проблеме!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    await update.message.reply_text("⏳ Думаю над ответом...")

    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, generate_reply, user_question)

    await update.message.reply_text(f"🤖 {answer}")

def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Telegram бот запущен! Ждёт сообщений...")
    app.run_polling()

# === Точка входа ===

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "telegram":
        run_telegram_bot()
    else:
        while True:
            q = input("Игрок спрашивает: ")
            answer = generate_reply(q)
            print(f"🤖 Ответ:\n{answer}\n")
