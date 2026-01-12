import sqlite3
from typing import Optional

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS distribution (
            telegram_id_sender INTEGER NOT NULL,
            telegram_id_recipient INTEGER NOT NULL,
            status INTEGER DEFAULT 0,
            PRIMARY KEY (telegram_id_sender, telegram_id_recipient)
        )
    """)
    conn.commit()
    conn.close()


def add_user(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str] = None,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, username, first_name, last_name),
    )
    conn.commit()
    conn.close()


def confirm_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
    """
        UPDATE users SET confirmed = 1 WHERE user_id = ?
    """,
        (user_id,),
    )
    conn.commit()
    conn.close()


def is_confirmed(user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT confirmed FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False


def get_confirmed_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE confirmed = 1")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users


def get_recipients_for_sender(sender_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.telegram_id_recipient, u.first_name, u.last_name, u.username, d.status
        FROM distribution d
        JOIN users u ON d.telegram_id_recipient = u.user_id
        WHERE d.telegram_id_sender = ?
    """, (sender_id,))
    recipients = cursor.fetchall()
    conn.close()
    return recipients


def get_user_contact(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        name = f"{result[0]} {result[1] or ''}".strip()
        username = result[2]
        if username:
            return f"@{username}" if not username.startswith("@") else username
        return name
    return f"ID: {user_id}"


def update_distribution_status(sender_id: int, recipient_id: int, status: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE distribution SET status = ? 
        WHERE telegram_id_sender = ? AND telegram_id_recipient = ?
    """, (status, sender_id, recipient_id))
    conn.commit()
    conn.close()


def take_letters_for_recipient(recipient_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT telegram_id_sender
        FROM distribution
        WHERE telegram_id_recipient = ? AND status = 1
    """,
        (recipient_id,),
    )
    senders = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        """
        UPDATE distribution SET status = 2
        WHERE telegram_id_recipient = ? AND status = 1
    """,
        (recipient_id,),
    )
    conn.commit()
    conn.close()
    return senders


def get_pending_letters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            d.telegram_id_sender,
            us.username,
            us.first_name,
            us.last_name,
            d.telegram_id_recipient,
            ur.username,
            ur.first_name,
            ur.last_name
        FROM distribution d
        JOIN users us ON us.user_id = d.telegram_id_sender
        JOIN users ur ON ur.user_id = d.telegram_id_recipient
        WHERE d.status = 1
        ORDER BY d.telegram_id_sender, d.telegram_id_recipient
    """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
