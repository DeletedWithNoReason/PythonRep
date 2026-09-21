data = [
    {"name": "Amoxicillin", "qty": 10, "category": "antibiotic", "temp": 4.0},
    {"name": "Vitamin C", "qty": 50, "category": "vitamin", "temp": 18.5},
    {"name": "Vaccine X", "qty": "5", "category": "vaccine", "temp": 2.0}, 
    {"name": "Ibuprofen", "qty": 20, "category": "unknown_cat", "temp": 30.0},
]

for item in data:
    name = item.get("name")
    qty = item.get("qty")
    category = item.get("category")
    temp = item.get("temp")

    if type(qty) is not int or type(temp) is not float:
        print(f"{name}: Data error")
        continue

    if temp < 5.0:
        temp_status = "Too cold"
    elif temp > 25.0:
        temp_status = "Too hot"
    else:
        temp_status = "Normal"

    match category:
        case "antibiotic":
            cat_status = "Prescription medication"
        case "vitamin":
            cat_status = "Over-the-counter"
        case "vaccine":
            cat_status = "Requires special storage"
        case _:
            cat_status = "Unknown category"

    print(f"{name} | Category: {cat_status} | Temperature: {temp_status}")