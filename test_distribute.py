import logging
from collections import defaultdict

from distribute import create_distribution, verify_distribution

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_pairs(distribution):
    pairs = []
    for sender, receivers in distribution.items():
        for receiver in receivers:
            pairs.append((sender, receiver))
    return sorted(pairs)


def log_pairs(distribution):
    pairs = get_pairs(distribution)
    logger.info("Пары (отправитель -> получатель):")
    for sender, receiver in pairs:
        logger.info(f"  {sender} -> {receiver}")
    logger.info(f"Всего пар: {len(pairs)}")
    return pairs


def test_empty_users():
    distribution = create_distribution([])
    assert distribution == {}


def test_single_user():
    users = [(1, "Иван", "Иванов")]
    distribution = create_distribution(users)
    assert distribution == {}


def test_two_users():
    users = [(1, "Иван", "Иванов"), (2, "Петр", "Петров")]
    logger.info(f"Тест: {len(users)} пользователя, k=1")
    distribution = create_distribution(users, k=1)

    assert len(distribution) == 2
    assert 1 in distribution
    assert 2 in distribution

    pairs = get_pairs(distribution)
    assert len(pairs) == 2
    assert (1, 2) in pairs or (2, 1) in pairs

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 1
    assert stats["incoming_count"] == 1
    assert stats["total_users"] == 2

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)


def test_three_users():
    users = [(1, "Иван", "Иванов"), (2, "Петр", "Петров"), (3, "Сидор", "Сидоров")]
    logger.info(f"Тест: {len(users)} пользователя, k=1")
    distribution = create_distribution(users, k=1)

    assert len(distribution) == 3

    pairs = get_pairs(distribution)
    assert len(pairs) == 3
    assert len(set(pairs)) == 3

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 1
    assert stats["incoming_count"] == 1
    assert stats["total_users"] == 3

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)


def test_four_users_default_k():
    users = [
        (1, "Иван", "Иванов"),
        (2, "Петр", "Петров"),
        (3, "Сидор", "Сидоров"),
        (4, "Мария", "Иванова"),
    ]
    logger.info(f"Тест: {len(users)} пользователя, k по умолчанию (n//2)")
    distribution = create_distribution(users)

    assert len(distribution) == 4

    pairs = get_pairs(distribution)
    assert len(pairs) == 8

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 2
    assert stats["incoming_count"] == 2
    assert stats["total_users"] == 4

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)


def test_five_users_custom_k():
    users = [
        (1, "Иван", "Иванов"),
        (2, "Петр", "Петров"),
        (3, "Сидор", "Сидоров"),
        (4, "Мария", "Иванова"),
        (5, "Анна", "Петрова"),
    ]
    logger.info(f"Тест: {len(users)} пользователей, k=2")
    distribution = create_distribution(users, k=2)

    assert len(distribution) == 5

    pairs = get_pairs(distribution)
    assert len(pairs) == 10

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 2
    assert stats["incoming_count"] == 2
    assert stats["total_users"] == 5

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)


def test_ten_users():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 11)]
    logger.info(f"Тест: {len(users)} пользователей, k по умолчанию (n//2)")
    distribution = create_distribution(users)

    assert len(distribution) == 10

    pairs = get_pairs(distribution)
    assert len(pairs) == 50

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 5
    assert stats["incoming_count"] == 5
    assert stats["total_users"] == 10

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)


def test_all_users_have_same_outgoing_count():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 8)]
    logger.info(
        f"Тест: проверка одинакового количества исходящих, {len(users)} пользователей, k=3"
    )
    distribution = create_distribution(users, k=3)

    outgoing_counts = [len(receivers) for receivers in distribution.values()]
    assert len(set(outgoing_counts)) == 1
    assert outgoing_counts[0] == 3
    logger.info(
        f"Все пользователи имеют одинаковое количество исходящих: {outgoing_counts[0]}"
    )


def test_all_users_have_same_incoming_count():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 8)]
    logger.info(
        f"Тест: проверка одинакового количества входящих, {len(users)} пользователей, k=3"
    )
    distribution = create_distribution(users, k=3)

    incoming = defaultdict(int)
    for receivers in distribution.values():
        for receiver in receivers:
            incoming[receiver] += 1

    incoming_counts = list(incoming.values())
    assert len(set(incoming_counts)) == 1
    assert incoming_counts[0] == 3
    logger.info(
        f"Все пользователи имеют одинаковое количество входящих: {incoming_counts[0]}"
    )


def test_no_self_messages():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 6)]
    logger.info(f"Тест: проверка отсутствия самописем, {len(users)} пользователей, k=2")
    distribution = create_distribution(users, k=2)

    for sender, receivers in distribution.items():
        assert sender not in receivers
    logger.info("Проверка пройдена: нет самописем")


def test_k_larger_than_n_minus_one():
    users = [(1, "Иван", "Иванов"), (2, "Петр", "Петров"), (3, "Сидор", "Сидоров")]
    logger.info(
        f"Тест: k больше n-1, {len(users)} пользователя, k=10 (должно быть ограничено до n-1=2)"
    )
    distribution = create_distribution(users, k=10)

    assert len(distribution) == 3

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 2
    assert stats["incoming_count"] == 2
    logger.info(
        f"k было ограничено: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )


def test_verify_empty_distribution():
    is_valid, stats = verify_distribution({})
    assert not is_valid
    assert stats == {}


def test_distribution_consistency():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 7)]
    logger.info(
        f"Тест: проверка консистентности распределения, {len(users)} пользователей, k=2, 10 итераций"
    )

    for i in range(10):
        distribution = create_distribution(users, k=2)
        is_valid, stats = verify_distribution(distribution)
        assert is_valid
        assert stats["outgoing_count"] == 2
        assert stats["incoming_count"] == 2
        logger.debug(f"Итерация {i + 1}: распределение корректно")
    logger.info("Все 10 итераций прошли успешно")


def test_odd_number_of_users():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 9)]
    distribution = create_distribution(users)

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 4
    assert stats["incoming_count"] == 4


def test_even_number_of_users():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 10)]
    distribution = create_distribution(users)

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 4
    assert stats["incoming_count"] == 4


def test_twenty_users():
    users = [(i, f"User{i}", f"Last{i}") for i in range(1, 21)]
    logger.info(f"Тест: {len(users)} пользователей, k по умолчанию (n//2)")
    distribution = create_distribution(users)

    assert len(distribution) == 20

    pairs = get_pairs(distribution)
    assert len(pairs) == 200

    is_valid, stats = verify_distribution(distribution)
    assert is_valid
    assert stats["outgoing_count"] == 10
    assert stats["incoming_count"] == 10
    assert stats["total_users"] == 20

    logger.info(
        f"Статистика: исходящих={stats['outgoing_count']}, входящих={stats['incoming_count']}"
    )
    log_pairs(distribution)
