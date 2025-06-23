# GoK_Helper_bot

🤖 **GoK_Helper_bot** — это умный Telegram бот поддержки для игры **Game of Khans**, который:
- Использует **базу из ~50,000 реальных кейсов игроков** за 5 лет.
- Автоматически ищет похожие обращения в Google Sheets.
- Генерирует ответы с помощью OpenAI GPT.
- Работает как интерактивный скрипт и как Telegram бот.

## 📂 Структура
- `main.py` — основной код бота
- `config.json` — конфигурация ключей (НЕ пушить в Git!)
- `requirements.txt` — зависимости Python
- `.gitignore` — игнорирует `venv` и ключи

## ⚙️ **Что внутри `config.json`**


## 🚀 Запуск
1. Создать виртуальное окружение:
python3 -m venv venv
source venv/bin/activate
2. Установить зависимости:
pip install -r requirements.txt
3. Запустить локально:
python main.py
4. Запустить Telegram-бота:

Файл `config.json` хранит ключи и настройки:
```json
{
  "spreadsheet_id": "<ID твоего Google Sheets>",
  "range_name": "Sheet1!A1:E49226",
  "google_service_account_file": "/путь/к/твоему/google-creds.json",
  "openai_api_key": "<ТВОЙ_OPENAI_API_KEY>",
  "telegram_token": "<ТВОЙ_TELEGRAM_BOT_TOKEN>"
}

