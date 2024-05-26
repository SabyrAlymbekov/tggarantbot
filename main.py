from aiogram import Bot, Dispatcher, executor, types
#import os
import sqlite3
#import json
from decimal import Decimal
import database
from connector import get_connector
from pytonconnect import TonConnect

import config
from message import get_comment_message
from connector import get_connector
from tc_storage import TcStorage
import asyncio

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)

# базы данных
db_path = 'database.db'
conn = database.create_connection(db_path)
cursor = conn.cursor()

# таблицы
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        ton_balance REAL DEFAULT 0,
        not_balance REAL DEFAULT 0,
        ton_address TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY,
        buyer_id INTEGER,
        seller_id INTEGER,
        ton_amount REAL,
        not_amount REAL,
        status TEXT,
        comments TEXT
    )
''')

conn.commit()


# НАЧАЛО РАБОТЫ БЛ
@dp.message_handler(commands=['start'])
async def start(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    await bot.send_message(message.chat.id, 'Добро пожаловать!')
    # Ton connector
    connector = get_connector(user_id)
    connected = await connector.restore_connection()
    markup = types.InlineKeyboardMarkup()
    print(connected)
    if user is None:
        # ТУТ МЫ ДОЛЖНЫ ДОДУМАТЬ РЕГИСТРАЦИЮ. P.S. все итак норм надо только кошелек привязать P.S я не пон как использовать database.create_user
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (user_id))
        conn.commit()
        print("newbie")
    if connected:
        print("connected")
    else:
        wallets_list = TonConnect.get_wallets()
        for wallet in wallets_list:
            markup.add(types.InlineKeyboardButton(wallet['name'], callback_data=f'connect:{wallet["name"]}'))
        await bot.reply_to(message, 'Подключите или переподключите пожалуйста свой TON кошелек', reply_markup=markup)
    await show_main_menu(message)

# МЕ1Н МЕНЮ
async def show_main_menu(message):
    user_id = message.from_user.id
    cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (user_id,))
    role = cursor.fetchone()[0]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == 'buyer':
        markup.add(types.KeyboardButton('Создать сделку'), types.KeyboardButton('Мои сделки'))
    else:
        markup.add(types.KeyboardButton('Мои сделки'), types.KeyboardButton('Создать сделку'))
    await bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=markup)


# СОЗДАНИЕ СДЕЛКИ КОМАНДА /create_deal
@bot.message_handler(func=lambda message: message.text == 'Создать сделку')
def create_deal(message):
    user_id = message.from_user.id

    # ПРИНЯТИЕ ТОНА
    bot.send_message(message.chat.id, 'Введите сумму TON:')
    bot.register_next_step_handler(message, process_ton_amount)


def process_ton_amount(message):
    user_id = message.from_user.id
    ton_amount = message.text
    try:
        ton_amount = Decimal(ton_amount)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат суммы!')
        return

    # ПРОВЕРКА БАЛАНСА
    cursor.execute("SELECT ton_balance FROM users WHERE telegram_id = ?", (user_id,))
    ton_balance = cursor.fetchone()[0]
    if ton_amount > ton_balance:
        bot.send_message(message.chat.id, 'Недостаточно средств!')
        return

    # ЛОГИКА СОЗДАНИЯ СДЕЛКИ, ОТПРАВКА ЕЕ В БД И ПРОДАЦУ, САМОЕ БЛ ТРУДНОЕ

    # КОГДА УЖЕ СОРЗДАЛИ ДЕЛКУ
    bot.send_message(message.chat.id, 'Сделка создана!')
    show_main_menu(message)


# МОИ СДЕЛКИ КОМАНДА /my_deals
@bot.message_handler(func=lambda message: message.text == 'Мои сделки')
def my_deals(message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM deals WHERE buyer_id = ? OR seller_id = ?", (user_id, user_id))
    deals = cursor.fetchall()

    if not deals:
        bot.send_message(message.chat.id, 'У вас нет активных сделок.')
        return

    for deal in deals:
        deal_id, buyer_id, seller_id, ton_amount, not_amount, status, comments = deal
        buyer_name = get_user_name(buyer_id)
        seller_name = get_user_name(seller_id)

        deal_info = f"Сделка #{deal_id}\n"
        deal_info += f"Покупатель: {buyer_name}\n"
        deal_info += f"Продавец: {seller_name}\n"
        deal_info += f"Сумма TON: {ton_amount}\n"
        deal_info += f"Статус: {status}\n"
        if comments:
            deal_info += f"Комментарии: {comments}\n"

        bot.send_message(message.chat.id, deal_info)
    show_main_menu(message)


# ПОЛУЧЕНИЕ ИП ПО АЙДИ ДЛЯ ПРОВЕДЕНИЯ СДЕЛКИ Я УСТАЛ УЖЕ ПИСАТЬ КОДДЖДДДДДЛДДДДД
def get_user_name(user_id):
    cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return f"@{user[0]}"
    else:
        return 'Неизвестный пользователь'

# ТОН ПОПОЛНЕНИЕ

# end

#def send_message_to_seller(seller_id, message):


asyncio.run(bot.polling(none_stop=True))