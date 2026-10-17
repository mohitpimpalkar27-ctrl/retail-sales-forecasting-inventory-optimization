from src.simulation import simulate_policy

def test_no_negative_stock_and_flow_balance():
    result = simulate_policy([5, 10, 4, 7], [6, 6, 6, 6], 12, 2)
    assert (result.closing_stock >= 0).all()
    assert (result.opening_stock - result.units_sold == result.closing_stock).all()
    assert (result.units_sold + result.lost_units == result.demand).all()
