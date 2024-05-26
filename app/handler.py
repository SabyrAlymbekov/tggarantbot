import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from decimal import Decimal
from pytonconnect import TonConnect
from replenishment.connector import get_connector
#import database
import app.keyboards as kb
from pytoniq_core import Address
import logging

# Initialize bot and dispatcher

router = Router()

logger = logging.getLogger(__file__)

db_path = 'database.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
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

# Start command handler
@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    await message.answer('Добро пожаловать!')

    # Ton connector
    connector = get_connector(chat_id)
    connected = await connector.restore_connection()
    print(connected)
    if user is None:
        # User registration logic
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (user_id,))
        conn.commit()
        print("newbie")

    if connected:
        await show_main_menu(message)
    else:
        await message.answer('Подключите или переподключите пожалуйста свой TON кошелек', reply_markup=kb.wallets)


# Main menu
async def show_main_menu(message: Message):
    user_id = message.from_user.id
    await message.answer('Что вы хотите сделать?', reply_markup=kb.main)

# wallet connect func
async def connect_wallet(message: Message, wallet_name: str):
    chat_id = message.chat.id
    connector = await get_connector(chat_id)
    wallets_list = await connector.get_wallets()
    wallet = None

    for w in wallets_list:
        if w['name'] == wallet_name:
            wallet = w

    if wallet is None:
        raise Exception(f'Unknown wallet: {wallet_name}')

    print(f"Содержимое wallet: {wallet}")
    print("work_prev")
    try:
        generated_url = await connector.connect(wallet)
        print(generated_url)
    except Exception as e:
        print(f"Ошибка при подключении: {e}")
        return
    print("work_next")
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='Connect', url=generated_url)

    await message.answer(text='Connect wallet within 3 minutes', reply_markup=mk_b.as_markup())

    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='Start', callback_data='start')

    for i in range(1, 180):
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                wallet_address = connector.account.address
                wallet_address = Address(wallet_address).to_str(is_bounceable=False)
                await message.answer(f'You are connected with address <code>{wallet_address}</code>', reply_markup=mk_b.as_markup())
                logger.info(f'Connected with address: {wallet_address}')
            return

    await message.answer(f'Timeout error!', reply_markup=mk_b.as_markup())

# 
@router.callback_query(lambda call: True)
async def main_callback_handler(call: CallbackQuery):
    await call.answer()
    message = call.message
    data = call.data
    if data == "start":
        await start(message)
    else:
        data = data.split(':')
        if data[0] == 'connect':
            await connect_wallet(message, data[1])

# # Create deal command handler
# @router.message(F.text == 'Создать сделку')
# async def create_deal(message: Message):
#     user_id = message.from_user.id
#     await message.answer('Введите сумму TON:')
#     router.register_message_handler(process_ton_amount, state="waiting_for_ton_amount")

async def process_ton_amount(message: Message):
    user_id = message.from_user.id
    ton_amount = message.text
    try:
        ton_amount = Decimal(ton_amount)
    except ValueError:
        await message.answer('Неверный формат суммы!')
        return

    # Check balance
    cursor.execute("SELECT ton_balance FROM users WHERE telegram_id = ?", (user_id,))
    ton_balance = cursor.fetchone()[0]
    if ton_amount > ton_balance:
        await message.answer('Недостаточно средств!')
        return

    # Deal creation logic
    await message.answer('Сделка создана!')
    await show_main_menu(message)


async def process_ton_amount(message: Message):
    user_id = message.from_user.id
    ton_amount = message.text
    try:
        ton_amount = Decimal(ton_amount)
    except ValueError:
        await message.answer('Неверный формат суммы!')
        return

    # Check balance
    cursor.execute("SELECT ton_balance FROM users WHERE telegram_id = ?", (user_id,))
    ton_balance = cursor.fetchone()[0]
    if ton_amount > ton_balance:
        await message.answer('Недостаточно средств!')
        return

    # Deal creation logic
    await message.answer('Сделка создана!')
    await show_main_menu(message)


# My deals command handler
@router.message(F.text == 'Мои сделки')
async def my_deals(message: Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM deals WHERE buyer_id = ? OR seller_id = ?", (user_id, user_id))
    deals = cursor.fetchall()

    if not deals:
        await message.answer('У вас нет активных сделок.')
        return

    for deal in deals:
        deal_id, buyer_id, seller_id, ton_amount, not_amount, status, comments = deal
        buyer_name = await get_user_name(buyer_id)
        seller_name = await get_user_name(seller_id)

        deal_info = f"Сделка #{deal_id}\n"
        deal_info += f"Покупатель: {buyer_name}\n"
        deal_info += f"Продавец: {seller_name}\n"
        deal_info += f"Сумма TON: {ton_amount}\n"
        deal_info += f"Статус: {status}\n"
        if comments:
            deal_info += f"Комментарии: {comments}\n"

        await message.answer(deal_info)
    await show_main_menu(message)


# Get user name by ID
async def get_user_name(user_id):
    cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return f"@{user[0]}"
    else:
        return 'Неизвестный пользователь'

