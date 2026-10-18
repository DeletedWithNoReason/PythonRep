from datetime import datetime
from functools import wraps

VALID_TYPES = {"GATE", "CARGO", "ACCESS", "ALARM", "SENSOR", "CALL", "SYSTEM"}

def validate_line(line):
    if not line.strip():
        return False, "empty"

    parts = line.split("|")
    if len(parts) < 2:
        return False, "invalid_structure"

    time_str = parts[0]
    event_type = parts[1]

    try:
        datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return False, "invalid_time"

    if event_type not in VALID_TYPES:
        return False, "invalid_type"

    for part in parts[2:]:
        if "=" not in part or part.startswith("=") or part.endswith("="):
            return False, "invalid_kv"

    return True, "valid"


def corrupted_filter(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        corrupted_count = 0

        for line in func(*args, **kwargs):
            if not line.strip():
                continue

            is_valid, _ = validate_line(line)
            if is_valid:
                yield line
            else:
                corrupted_count += 1

        wrapper.corrupted_count = corrupted_count

    wrapper.corrupted_count = 0
    return wrapper


def statistics_report(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        type_counts = {t: 0 for t in VALID_TYPES}

        for line in func(*args, **kwargs):
            parts = line.split("|")
            if len(parts) >= 2:
                event_type = parts[1]
                if event_type in type_counts:
                    type_counts[event_type] += 1

        corrupted_count = getattr(func, "corrupted_count", 0)

        print("\n" + "=" * 45)
        print("          ФІНАЛЬНИЙ ЗВІТ СЕРВЕРА ХАБУ")
        print("=" * 45)
        for ev_type, count in type_counts.items():
            print(f" Тип {ev_type:<10}: {count} подій")
        print("-" * 45)
        print(f" Кількість битих рядків: {corrupted_count}")
        print("=" * 45 + "\n")

    return wrapper


def transaction_stream(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()


@statistics_report
@corrupted_filter
def process_hub_logs(file_path):
    return transaction_stream(file_path)


if __name__ == "__main__":
    file_name = "hub_log.txt"
    process_hub_logs(file_name)