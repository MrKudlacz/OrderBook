import pytest
from tests_jsons import ORDERS_SAMPLE_TEST_JSON as sample_tests
from tests_jsons import ORDERS_VERIFY_TEST_JSON as verify_tests
from main import OrdersHandler, OutputMaker
import json

BOOKING_DB_PATH = r"orders.db"


@pytest.fixture()
def order_book():
    order_book_inst = OrdersHandler(BOOKING_DB_PATH)
    return order_book_inst


@pytest.fixture()
def output_maker():
    output_maker_inst = OutputMaker()
    return output_maker_inst


@pytest.mark.parametrize("tests_key", sample_tests.keys())
def test_sample_orders(order_book, output_maker, tests_key):
    if sample_tests[tests_key]["reset"]:
        order_book.reset_table(BOOKING_DB_PATH)
    order_df = order_book.receive_order(sample_tests[tests_key]["input"])
    buy_orders, sell_orders = order_book.fetch_current_state()
    state_json = output_maker.print_prettifier(buy_orders, sell_orders)
    transactions_json = order_book.transaction_message
    assert state_json == json.loads(sample_tests[tests_key]["state"])
    assert str(transactions_json) == str(
        json.loads(sample_tests[tests_key]["transactions"])
    )


@pytest.mark.parametrize("tests_key", verify_tests.keys())
def test_verify_orders(order_book, output_maker, tests_key):
    if verify_tests[tests_key]["reset"]:
        order_book.reset_table(BOOKING_DB_PATH)
    order_df = order_book.receive_order(verify_tests[tests_key]["input"])
    buy_orders, sell_orders = order_book.fetch_current_state()
    state_json = output_maker.print_prettifier(buy_orders, sell_orders)
    transactions_json = order_book.transaction_message
    if verify_tests[tests_key]["final"]:
        assert state_json == json.loads(verify_tests[tests_key]["state"])
