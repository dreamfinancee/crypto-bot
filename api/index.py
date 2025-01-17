import os
import requests
from telegram import Update, Bot
from telegram.ext import CallbackContext, Dispatcher, CommandHandler

# Reemplaza 'YOUR TELEGRAM TOKEN HERE' con tu token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '')
bot = Bot(token=TELEGRAM_API_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Diccionario para almacenar las alertas
alerts = {}

def get_crypto_price(symbol):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data[symbol]['usd']  # Devuelve el precio en USD

def alert(update: Update, context: CallbackContext):
    try:
        crypto, value = context.args
        value = float(value)
        chat_id = update.effective_chat.id

        if chat_id not in alerts:
            alerts[chat_id] = []

        alerts[chat_id].append((crypto, value))

        update.message.reply_text(f'Alerta configurada para {crypto} a {value} USD')
    
    except ValueError:
        update.message.reply_text('Error: Usa el comando /alert seguido del nombre del activo y el valor.')

def check_alerts(context: CallbackContext):
    for chat_id in alerts:
        for crypto, value in alerts[chat_id][:]:
            current_price = get_crypto_price(crypto)
            if current_price >= value:
                context.bot.send_message(chat_id=chat_id, text=f'¡Alerta! {crypto} alcanzó los {value} USD.')
                alerts[chat_id].remove((crypto, value))

dispatcher.add_handler(CommandHandler('alert', alert))

# Esta función será llamada por Vercel
def main_handler(event, context):
    # Maneja la lógica de webhook aquí
    return "Bot is running!"

# Llama a la función check_alerts cada 60 segundos
import time
import threading

def run_check_alerts():
    while True:
        check_alerts(None)
        time.sleep(60)

threading.Thread(target=run_check_alerts).start()
  
