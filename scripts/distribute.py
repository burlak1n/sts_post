import random
import sqlite3
from collections import defaultdict
from typing import Dict, List, Tuple

DB_NAME = "users.db"


def recreate_distribution_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS distribution")
    cursor.execute("""
        CREATE TABLE distribution (
            telegram_id_sender INTEGER NOT NULL,
            telegram_id_recipient INTEGER NOT NULL,
            status INTEGER DEFAULT 0,
            PRIMARY KEY (telegram_id_sender, telegram_id_recipient)
        )
    """)
    conn.commit()
    conn.close()


def save_distribution(distribution: Dict[int, List[int]]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for sender_id, receivers in distribution.items():
        for receiver_id in receivers:
            cursor.execute("""
                INSERT INTO distribution (telegram_id_sender, telegram_id_recipient, status)
                VALUES (?, ?, 0)
            """, (sender_id, receiver_id))
    conn.commit()
    conn.close()


def get_all_confirmed_users() -> List[Tuple[int, str, str]]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, first_name, last_name FROM users WHERE confirmed = 1"
    )
    users = cursor.fetchall()
    conn.close()
    return users


def create_distribution(
    users: List[Tuple[int, str, str]], k: int = None
) -> Dict[int, List[int]]:
    if not users:
        return {}

    if len(users) < 2:
        return {}

    user_ids = [user[0] for user in users]
    n = len(user_ids)

    if k is None:
        k = max(1, n // 2)

    k = min(k, n - 1)

    random.shuffle(user_ids)

    distribution = defaultdict(list)

    for i, sender_id in enumerate(user_ids):
        for j in range(1, k + 1):
            receiver_idx = (i + j) % n
            receiver_id = user_ids[receiver_idx]
            distribution[sender_id].append(receiver_id)

    return dict(distribution)


def verify_distribution(
    distribution: Dict[int, List[int]],
) -> Tuple[bool, Dict[str, int]]:
    if not distribution:
        return False, {}

    outgoing = defaultdict(int)
    incoming = defaultdict(int)

    for sender, receivers in distribution.items():
        outgoing[sender] = len(receivers)
        for receiver in receivers:
            incoming[receiver] += 1

    outgoing_counts = list(outgoing.values())
    incoming_counts = list(incoming.values())

    all_outgoing_same = len(set(outgoing_counts)) == 1 if outgoing_counts else False
    all_incoming_same = len(set(incoming_counts)) == 1 if incoming_counts else False

    stats = {
        "outgoing_count": outgoing_counts[0] if outgoing_counts else 0,
        "incoming_count": incoming_counts[0] if incoming_counts else 0,
        "total_users": len(distribution),
    }

    return all_outgoing_same and all_incoming_same, stats


def print_distribution(
    distribution: Dict[int, List[int]], users_data: List[Tuple[int, str, str]]
):
    user_map = {user[0]: f"{user[1]} {user[2] or ''}".strip() for user in users_data}

    print("\nРаспределение:\n")
    for sender_id, receivers in sorted(distribution.items()):
        sender_name = user_map.get(sender_id, f"ID: {sender_id}")
        receiver_names = [user_map.get(rid, f"ID: {rid}") for rid in receivers]
        print(f"{sender_name} (ID: {sender_id}) пишет:")
        for name in receiver_names:
            print(f"  - {name}")
        print()


def main():
    users = get_all_confirmed_users()

    if not users:
        print("Нет подтвержденных пользователей")
        return

    print(f"Найдено подтвержденных пользователей: {len(users)}")

    if len(users) < 2:
        print("Нужно минимум 2 пользователя для распределения")
        return

    recreate_distribution_table()

    # k = min(5, max(1, len(users) // 4))
    k = 3
    distribution = create_distribution(users, k)

    save_distribution(distribution)

    is_valid, stats = verify_distribution(distribution)

    if is_valid:
        print("✓ Распределение корректно")
        print(f"  Каждый пишет: {stats['outgoing_count']} человек(а)")
        print(f"  Каждый получает от: {stats['incoming_count']} человек(а)")
    else:
        print("⚠ Распределение некорректно")

    print_distribution(distribution, users)

    print("\nСтатистика:")
    print(f"  Всего пользователей: {stats['total_users']}")
    print(f"  Исходящих писем на человека: {stats['outgoing_count']}")
    print(f"  Входящих писем на человека: {stats['incoming_count']}")


if __name__ == "__main__":
    main()
