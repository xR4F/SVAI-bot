import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
from io import StringIO

# === НАСТРОЙКИ ===
TOKEN = "7301662713:AAFGXo6q1T9UQ8wu0j2C2qCKh4thCv6bGG0"
SPREADSHEET_NAME = "Заявки дилеров Свай-Фундамент (Телеграм-бот)"

# Получаем JSON-ключ из переменной окружения
google_key_str = os.environ["GOOGLE_KEY_JSON"]
google_key = json.loads(google_key_str)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_key, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

bot = telebot.TeleBot(TOKEN)
user_data = {}

dealers = ["Степа", "Андрей сосед", "Андрей диллер", "Опора Сибири", "Костя диллер"]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    markup = InlineKeyboardMarkup()
    for d in dealers:
        markup.add(InlineKeyboardButton(d, callback_data=f"dealer_{d}"))
    bot.send_message(user_id, "Выбери дилера:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dealer_"))
def handle_dealer(call):
    user_id = call.message.chat.id
    dealer_name = call.data.split("_", 1)[1]
    user_data[user_id]["dealer"] = dealer_name
    user_data[user_id]["order_date"] = datetime.now().strftime("%d.%m.%Y")
    bot.send_message(user_id, "Введи дату отгрузки (например: 15.07.2025):")
    bot.register_next_step_handler(call.message, handle_ship_date)

def handle_ship_date(message):
    user_id = message.chat.id
    user_data[user_id]["ship_date"] = message.text
    bot.send_message(user_id, "Введи позицию 1:")
    bot.register_next_step_handler(message, lambda m: handle_position(m, 1))

def handle_position(message, pos_num):
    user_id = message.chat.id
    user_data[user_id][f"position{pos_num}"] = message.text
    bot.send_message(user_id, f"Введи количество {pos_num}:")
    bot.register_next_step_handler(message, lambda m: handle_quantity(m, pos_num))

def handle_quantity(message, pos_num):
    user_id = message.chat.id
    user_data[user_id][f"quantity{pos_num}"] = message.text
    if pos_num < 3:
        bot.send_message(user_id, f"Введи позицию {pos_num+1}:")
        bot.register_next_step_handler(message, lambda m: handle_position(m, pos_num+1))
    else:
        bot.send_message(user_id, "Введи примечание:")
        bot.register_next_step_handler(message, handle_note)

def handle_note(message):
    user_id = message.chat.id
    user_data[user_id]["note"] = message.text
    data = user_data[user_id]
    rows = []
    for i in range(1, 4):
        pos = data.get(f"position{i}")
        qty = data.get(f"quantity{i}")
        if pos and qty:
            if not rows:
                rows.append([data["order_date"], data["dealer"], data["ship_date"], pos, qty, data["note"]])
            else:
                rows.append(["", "", "", pos, qty, ""])
    for row in rows:
        sheet.append_row(row)
    bot.send_message(user_id, "✅ Заявка добавлена!")

bot.polling()
