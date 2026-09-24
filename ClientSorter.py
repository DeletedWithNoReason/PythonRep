def process_deals(deals):
    results = []

    for item in deals:
        amount = item.get("amount")
        status = item.get("status")

        if type(amount) not in (int, float) or type(amount) is bool:
            category = "Фальшиві дані"
        elif amount < 100:
            category = "Дрібнота"
        elif amount <= 999:
            category = "Середнячок"
        else:
            category = "Великий клієнт"

        match status:
            case "clean":
                decision = "Працювати без питань"
            case "suspicious":
                decision = "Перевірити документи"
            case "fraud":
                decision = "У чорний список"
            case _:
                decision = "Невідомий статус"

        results.append({
            "name": item.get("name"),
            "category": category,
            "decision": decision
        })

    return results


if __name__ == "__main__":
    test_deals = [
        {"name": "Олексій", "amount": 50, "status": "clean"},
        {"name": "Іван", "amount": 500, "status": "suspicious"},
        {"name": "Марія", "amount": 1500, "status": "fraud"},
        {"name": "Дмитро", "amount": "сто грн", "status": "clean"}
    ]
    print(process_deals(test_deals))