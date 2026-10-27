import pytest
from service_body_test import Order

def test_order_init_and_repr():
    items = [{'price': 100, 'quantity': 2}]
    order = Order(1, items)
    assert order.id == 1
    assert order.items == items
    assert repr(order) == "<Order 1: 1 items>"

def test_total_various_items():
    # Порожній список items
    order_empty = Order(1, [])
    assert order_empty.total() == 0

    # Один елемент
    order_single = Order(2, [{'price': 50, 'quantity': 3}])
    assert order_single.total() == 150

    # Кілька елементів
    order_multi = Order(3, [
        {'price': 10, 'quantity': 5},
        {'price': 20, 'quantity': 2}
    ])
    assert order_multi.total() == 90

def test_most_expensive():
    order = Order(1, [
        {'price': 10, 'quantity': 1},
        {'price': 50, 'quantity': 2},
        {'price': 30, 'quantity': 1}
    ])
    assert order.most_expensive() == {'price': 50, 'quantity': 2}

    # Межовий випадок: порожній список викликає ValueError у max()
    order_empty = Order(2, [])
    with pytest.raises(ValueError):
        order_empty.most_expensive()

def test_apply_discount_valid():
    items = [
        {'price': 100, 'quantity': 1},
        {'price': 200, 'quantity': 2}
    ]
    order = Order(1, items)
    
    # Знижка 10%
    order.apply_discount(10)
    assert order.items[0]['price'] == 90.0
    assert order.items[1]['price'] == 180.0

    # Межове значення: знижка 0%
    order.apply_discount(0)
    assert order.items[0]['price'] == 90.0

    # Межове значення: знижка 100%
    order.apply_discount(100)
    assert order.items[0]['price'] == 0.0
    assert order.items[1]['price'] == 0.0

def test_apply_discount_invalid():
    order = Order(1, [{'price': 100, 'quantity': 1}])
    
    # Невалідні значення (< 0 та > 100)
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(-1)

    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(101)