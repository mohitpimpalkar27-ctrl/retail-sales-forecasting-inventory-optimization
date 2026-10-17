from src.inventory import safety_stock, reorder_point, inventory_position, order_quantity

def test_inventory_math():
    assert safety_stock(0, 4) == 0
    assert reorder_point(40, 5, 50) == 250
    assert inventory_position(150, 50, 0) == 200
    assert order_quantity(200, 250, 400) == 200
    assert order_quantity(300, 250, 400) == 0
