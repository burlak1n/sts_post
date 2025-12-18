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
