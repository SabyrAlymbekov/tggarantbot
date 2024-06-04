import sqlite3
from typing import List, Optional

# Инициализация соединения с базой данных
def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # Создание таблицы users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL,
            deals TEXT NOT NULL,
            ton_address TEXT NOT NULL,
            ton_balance INTEGER NOT NULL,
            not_balance INTEGER NOT NULL,
            rub_balance INTEGER NOT NULL,
            usd_balance INTEGER NOT NULL
        )
    ''')

    # Создание таблицы deals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            cost INTEGER NOT NULL,
            comments TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (seller_id) REFERENCES users (telegram_id)
        )
    ''')

    conn.commit()
    conn.close()

# Конвертация списка в строку для хранения в БД
def list_to_string(lst: List[int]) -> str:
    return ','.join(map(str, lst))

# Конвертация строки в список для получения из БД
def string_to_list(s: str) -> List[int]:
    return list(map(int, s.split(','))) if s else []

# Добавление нового пользователя
def add_user(telegram_id: int, balance: int, deals: List[int], ton_address: str, ton_balance: int, not_balance: int, rub_balance: int, usd_bsalance: int):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, balance, deals, ton_address, ton_balance, not_balance, rub_balance, usd_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (telegram_id, balance, list_to_string(deals), ton_address, ton_balance, not_balance, rub_balance, usd_bsalance))
    conn.commit()
    conn.close()

# Получение данных о пользователе по telegram_id
def get_user(telegram_id: int) -> Optional[dict]:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'telegram_id': user[0],
            'balance': user[1],
            'deals': string_to_list(user[2]),
            'ton_address': user[3],
            'ton_balance': user[4],
            'not_balance': user[5],
            'rub_balance': user[6],
            'usd_balance': user[7]
        }
    return None

# Обновление данных пользователя
def update_user(telegram_id: int, balance: int, deals: List[int], ton_address: str, ton_balance: int, not_balance: int, rub_balance: int, usd_bsalance: int):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET balance = ?, deals = ?, ton_address = ?, ton_balance = ?, not_balance = ?, rub_balance = ?, usd_balance = ? WHERE telegram_id = ?
    ''', (balance, list_to_string(deals), ton_address, ton_balance, not_balance, rub_balance, usd_bsalance, telegram_id))
    conn.commit()
    conn.close()

# Добавление новой сделки
def add_deal(seller_id: int, cost: int, comments: List[int], name: str, description: str, deal_type: str):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deals (seller_id, cost, comments, name, description, type) VALUES (?, ?, ?, ?, ?, ?)
    ''', (seller_id, cost, list_to_string(comments), name, description, deal_type))
    deal_idn = cursor.lastrowid
    conn.commit()
    conn.close()
    return deal_idn

# def get_deals_by_seller(user_id: int) -> List[dict]:
#     conn = sqlite3.connect('app.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM deals WHERE seller_id = ?', (user_id,))
#     deals = cursor.fetchall()
#     conn.close()
#     return [
#         {
#             'deal_id': deal[0],
#             'seller_id': deal[1],
#             'cost': deal[2],
#             'comments': string_to_list(deal[3]),
#             'name': deal[4],
#             'description': deal[5],
#             'type': deal[6]
#         }
#         for deal in deals
#     ]

# Получение данных о сделке по deal_id
def get_deal(deal_id: int) -> Optional[dict]:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM deals WHERE deal_id = ?', (deal_id,))
    deal = cursor.fetchone()
    conn.close()
    if (deal):
        return {
            'deal_id': deal[0],
            'seller_id': deal[1],
            'cost': deal[2],
            'comments': string_to_list(deal[3]),
            'name': deal[4],
            'description': deal[5],
            'type': deal[6]
        }
    return None
def update_deal(deal_id: int, seller_id: int, cost: int, comments: List[int], name: str, description: str, deal_type: str):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE deals SET seller_id = ?, cost = ?, comments = ?, name = ?, description = ?, type = ? WHERE deal_id = ?
    ''', (seller_id, cost, list_to_string(comments), name, description, deal_type, deal_id))
    conn.commit()
    conn.close()

async def delete_deal(deal_id: int):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deals WHERE deal_id = ?', (deal_id,))
    conn.commit()
    conn.close()

def get_active_deals(deal_type: str) -> List[dict]:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM deals WHERE type = ?', (deal_type,))
    deals = cursor.fetchall()
    conn.close()
    return [
        {
            'deal_id': deal[0],
            'seller_id': deal[1],
            'cost': deal[2],
            'comments': string_to_list(deal[3]),
            'name': deal[4],
            'description': deal[5],
            'type': deal[6]
        }
        for deal in deals
    ]