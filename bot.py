import requests
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = '8744753502:AAHlPvqcuLmi2bPd2ck_FGe1xasenwG45cc'
SMS_API_KEY = 'ТВОЙ_SMS_ACTIVATE_API_KEY'

bot = TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📱 Запросить номер", callback_data="buy_number"))
    bot.reply_to(message, "👋 Привет! Нажми на кнопку ниже, чтобы получить виртуальный номер:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "buy_number")
def buy_number(call):
    bot.answer_callback_query(call.id, "Запрашиваем номер...")
    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getNumber&service=tg&country=10"
    try:
        response = requests.get(url).text
        if "ACCESS_NUMBER" in response:
            parts = response.split(":")
            activation_id = parts[1]
            phone_number = parts[2]
            text = f"📱 **Ваш номер:** `{phone_number}`\n\nОжидаем SMS с кодом..."
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔄 Проверить SMS", callback_data=f"check_{activation_id}"))
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, f"❌ Не удалось получить номер. Ответ сервиса: `{response}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка подключения к API: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_status(call):
    activation_id = call.data.split("_")[1]
    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getStatus&id={activation_id}"
    try:
        response = requests.get(url).text
        if "STATUS_OK" in response:
            code = response.split(":")[1]
            bot.send_message(call.message.chat.id, f"🔑 **Код получен:** `{code}`", parse_mode="Markdown")
        elif "STATUS_WAIT_CODE" in response:
            bot.answer_callback_query(call.id, "⏳ SMS еще не пришла, попробуйте через 10-15 секунд.")
        else:
            bot.send_message(call.message.chat.id, f"ℹ️ Статус: `{response}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {e}")

bot.polling(none_stop=True)
