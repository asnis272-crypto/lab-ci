from unittest.mock import Mock

import pytest

from shop.cart import Cart, Item


def test_empty_cart_initial_state(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0.0


def test_add_single_item(empty_cart: Cart) -> None:
    empty_cart.add("notebook", price=50.0, qty=3)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 150.0


def test_add_same_item_accumulates_qty(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0, qty=1)
    empty_cart.add("book", price=200.0, qty=2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 600.0


def test_add_existing_item_keeps_original_price(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0, qty=1)
    empty_cart.add("book", price=350.0, qty=2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 600.0


def test_remove_item(populated_cart: Cart) -> None:
    populated_cart.remove("pen")
    assert populated_cart.items_count() == 2
    assert populated_cart.total() == 400.0


def test_remove_nonexistent_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("unknown")


def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("book", price=-10.0)


@pytest.mark.parametrize("qty", [0, -1, -5])
def test_add_non_positive_qty_raises(empty_cart: Cart, qty: int) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", price=100.0, qty=qty)


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 460.0),
        (10, 414.0),
        (25, 345.0),
        (50, 230.0),
        (100, 0.0),
    ],
)
def test_total_with_valid_discounts(populated_cart: Cart, discount: float, expected: float) -> None:
    assert populated_cart.total(discount_percent=discount) == pytest.approx(expected)


@pytest.mark.parametrize("discount", [-0.1, -15, 100.1, 150])
def test_total_with_invalid_discount_raises(populated_cart: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        populated_cart.total(discount_percent=discount)


def test_total_in_currency_with_mock(populated_cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    result = populated_cart.total_in("USD", rates)

    assert result == pytest.approx(11.5)
    rates.get_rate.assert_called_once_with("USD")


@pytest.mark.parametrize("bad_rate", [0.0, -40.0])
def test_total_in_invalid_rate_raises(populated_cart: Cart, bad_rate: float) -> None:
    rates = Mock()
    rates.get_rate.return_value = bad_rate

    with pytest.raises(ValueError, match="rate"):
        populated_cart.total_in("USD", rates)


def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_returns_highest_unit_price(populated_cart: Cart) -> None:
    populated_cart.add("laptop", price=25000.0, qty=1)
    result = populated_cart.most_expensive()
    assert result == Item(name="laptop", price=25000.0, qty=1)
