🚀 Инструкция по запуску Telegram-бота через Render (публичный репозиторий)

1. Создай публичный репозиторий на GitHub.
2. Загрузи туда эти файлы: bot.py и requirements.txt
3. НЕ загружай файл google_key.json!
4. На Render при создании сервиса:
   - Build Command: pip install -r requirements.txt
   - Start Command: python bot.py
5. В разделе "Environment" добавь переменную:
   Ключ: GOOGLE_KEY_JSON
   Значение: содержимое файла google_key.json (в одну строку, без переносов)
6. Запусти бота — он будет работать через polling (без webhook)

⚠️ Не забудь выдать доступ к Google Таблице сервисному аккаунту из ключа.
