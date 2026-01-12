import sqlite3
from collections import defaultdict

DB_NAME = "users.db"


def get_all_distribution():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.telegram_id_sender, d.telegram_id_recipient
        FROM distribution d
        ORDER BY d.telegram_id_sender
    """)
    pairs = cursor.fetchall()
    conn.close()
    
    distribution = defaultdict(list)
    for sender_id, recipient_id in pairs:
        distribution[sender_id].append(recipient_id)
    
    return dict(distribution)


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, last_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def print_distribution(distribution, users_data):
    user_map = {user[0]: f"{user[1]} {user[2] or ''}".strip() for user in users_data}

    print("\nРаспределение:\n")
    for sender_id, receivers in sorted(distribution.items()):
        sender_name = user_map.get(sender_id, f"ID: {sender_id}")
        receiver_names = [user_map.get(rid, f"ID: {rid}") for rid in receivers]
        print(f"{sender_name} (ID: {sender_id}) пишет:")
        for name in receiver_names:
            print(f"  - {name}")
        print()


def calculate_stats(distribution):
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
        "outgoing_count": outgoing_counts[0] if outgoing_counts and all_outgoing_same else None,
        "incoming_count": incoming_counts[0] if incoming_counts and all_incoming_same else None,
        "total_users": len(distribution),
    }

    return all_outgoing_same and all_incoming_same, stats


def main():
    distribution = get_all_distribution()
    
    if not distribution:
        print("Распределение не найдено в базе данных")
        return
    
    users = get_all_users()
    
    is_valid, stats = calculate_stats(distribution)
    
    if is_valid:
        print("✓ Распределение корректно")
        print(f"  Каждый пишет: {stats['outgoing_count']} человек(а)")
        print(f"  Каждый получает от: {stats['incoming_count']} человек(а)")
    else:
        print("⚠ Распределение некорректно")
    
    print_distribution(distribution, users)
    
    print("\nСтатистика:")
    print(f"  Всего пользователей: {stats['total_users']}")
    if stats['outgoing_count'] is not None:
        print(f"  Исходящих писем на человека: {stats['outgoing_count']}")
    if stats['incoming_count'] is not None:
        print(f"  Входящих писем на человека: {stats['incoming_count']}")


if __name__ == "__main__":
    main()






