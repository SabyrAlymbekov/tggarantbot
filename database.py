import sqlite3

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    return None


def create_table(conn, create_table_sql):
    """Создает таблицу"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")


def create_user(conn, user):
    """Добавляет нового пользователя"""
    sql = ''' INSERT INTO users(telegram_id, role)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def get_user(conn, telegram_id):
    """Получает данные пользователя по ID"""
    sql = ''' SELECT * FROM users WHERE telegram_id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (telegram_id,))
    return cur.fetchone()


def get_users(conn):
    """Получает список всех пользователей"""
    sql = ''' SELECT * FROM users '''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def create_deal(conn, deal):
    """Создает новую сделку"""
    sql = ''' INSERT INTO deals(buyer_id, seller_id, ton_amount, not_amount, status)
              VALUES(?, ?, ?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, deal)
    conn.commit()
    return cur.lastrowid


def get_deal(conn, deal_id):
    """Получает информацию о сделке по ID"""
    sql = ''' SELECT * FROM deals WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (deal_id,))
    return cur.fetchone()


def get_deals(conn, buyer_id=None, seller_id=None):
    """Получает список сделок"""
    sql = ''' SELECT * FROM deals '''
    if buyer_id:
        sql += f" WHERE buyer_id = {buyer_id}"
    if seller_id:
        if buyer_id:
            sql += f" OR seller_id = {seller_id}"
        else:
            sql += f" WHERE seller_id = {seller_id}"
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def update_deal_status(conn, deal_id, status):
    """Обновляет статус сделки"""
    sql = ''' UPDATE deals SET status = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (status, deal_id))
    conn.commit()


def add_deal_comment(conn, deal_id, comment):
    """Добавляет комментарий к сделке"""
    sql = ''' UPDATE deals SET comments = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (comment, deal_id))
    conn.commit()