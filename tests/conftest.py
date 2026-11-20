import pytest

from shop.cart import Cart


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()


@pytest.fixture
def populated_cart() -> Cart:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    cart.add("pen", price=15.0, qty=4)
    return cart
