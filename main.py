"""Main module, takes stdin from cmd interface, adds transactions to DB,
performs transactions if available, prints final results.
"""
from datetime import datetime
import json
import sqlalchemy as db
import pandas as pd

BOOKING_DB_PATH = r"orders.db"


class OrdersHandler:
    """Main class for handling orders in db and filtering them."""

    def __init__(self, booking_db_path) -> None:
        self.engine = db.create_engine(f"sqlite:///{booking_db_path}")
        with self.engine.connect():
            meta = db.MetaData(self.engine)
            meta.reflect()
            self._create_orders_table()
            self.orders_table = db.Table(
                "orders_table", meta, autoload=True, autoload_with=self.engine
            )
        self.transaction_message = []

    def reset_table(self, booking_db_path):
        """Resets db if requested (by default at the begining of cmd session.)

        Args:
            booking_db_path (str): url to db file.
        """
        self.engine = db.create_engine(f"sqlite:///{booking_db_path}")
        with self.engine.connect():
            meta = db.MetaData(self.engine)
            meta.reflect()
            meta.drop_all()
            meta.reflect()
            self._create_orders_table()
            self.orders_table = db.Table(
                "orders_table", meta, autoload=True, autoload_with=self.engine
            )

    def _create_orders_table(self):
        metadata = db.MetaData()
        orders_table = db.Table(
            "orders_table",
            metadata,
            db.Column("id", db.Integer, primary_key=True),
            db.Column("direction", db.String),
            db.Column("price", db.Integer),
            db.Column("quantity", db.Integer),
            db.Column("peak", db.Integer),
            db.Column("remaining", db.Integer),
            db.Column("timestamp", db.Integer, primary_key=True),
        )
        metadata.create_all(self.engine)
        return orders_table

    def receive_order(self, filtered_order):
        """Takes orders from cmd, puts them to DB, runs transactios.

        Args:
            filtered_order (dataframe): _description_

        Returns:
            _type_: _description_
        """
        order_df = self._create_order_df(filtered_order)
        order_df, matching_orders = self._process_transactions(order_df)
        self._update_database(matching_orders)
        self._update_database(order_df)
        return order_df

    def _create_order_df(self, filtered_order):
        order_df = pd.DataFrame(
            columns=[
                "id",
                "direction",
                "price",
                "quantity",
                "peak",
                "remaining",
                "timestamp",
            ]
        )
        order_dict = json.loads(filtered_order)
        new_row = order_dict["order"]
        new_row["timestamp"] = datetime.now().strftime("%Y%m%d%H%M%S")
        if (
            order_dict["type"] == "Iceberg"
            and order_dict["order"]["quantity"] > order_dict["order"]["peak"]
        ):
            new_row["remaining"] = (
                order_dict["order"]["quantity"] - order_dict["order"]["peak"]
            )
            new_row["quantity"] = order_dict["order"]["peak"]
            new_row["peak"] = order_dict["order"]["peak"]
        else:
            new_row["peak"] = 0
            new_row["remaining"] = 0

        order_df = order_df.append(new_row, ignore_index=True)
        order_df = pd.DataFrame(
            columns=[
                "id",
                "direction",
                "price",
                "quantity",
                "peak",
                "remaining",
                "timestamp",
            ]
        )
        order_dict = json.loads(filtered_order)
        new_row = order_dict["order"]
        new_row["timestamp"] = datetime.now().strftime("%Y%m%d%H%M%S")
        if (
            order_dict["type"] == "Iceberg"
            and order_dict["order"]["quantity"] > order_dict["order"]["peak"]
        ):
            new_row["remaining"] = (
                order_dict["order"]["quantity"] - order_dict["order"]["peak"]
            )
            new_row["quantity"] = order_dict["order"]["peak"]
            new_row["peak"] = order_dict["order"]["peak"]
        else:
            new_row["peak"] = 0
            new_row["remaining"] = 0

        order_df = order_df.append(new_row, ignore_index=True)
        return order_df

    def _update_database(self, order_df):
        order_df.drop(order_df[order_df.quantity == 0].index, inplace=True)
        with self.engine.connect():
            order_df.to_sql(
                "orders_table", self.engine, if_exists="append", index=False
            )

    def _process_transactions(self, order_df):
        self.transaction_message = []
        matching_orders = self._fetch_matching_orders(order_df)
        number_of_rows = len(matching_orders.index)
        r_no = 0
        any_match_found = True
        while any_match_found:
            any_match_found = False
            if r_no == number_of_rows:
                r_no = 0

            while r_no < number_of_rows and order_df["quantity"].loc[0] > 0:
                if matching_orders["quantity"].loc[r_no] > 0:
                    order_df.loc[0], matching_orders.loc[r_no] = self._deduct_qty(
                        order_df.loc[0], matching_orders.loc[r_no]
                    )
                    if matching_orders["remaining"].loc[r_no] > 0:
                        matching_orders.loc[r_no] = self._move_reserve(
                            matching_orders.loc[r_no]
                        )
                    if (
                        order_df["remaining"].loc[0] > 0
                        and order_df["quantity"].loc[0] == 0
                    ):
                        order_df.loc[0] = self._move_reserve(order_df.loc[0])
                    if (
                        matching_orders["quantity"].loc[r_no] == 0
                        or r_no == (number_of_rows - 1)
                        or matching_orders["price"].loc[r_no]
                        == matching_orders["price"].loc[r_no + 1]
                    ):
                        r_no = r_no + 1
                    any_match_found = True
        return order_df, matching_orders

    def _move_reserve(self, order_df):
        quantity_to_move_from_reserve = min(order_df["peak"], order_df["remaining"])
        remaining_quantity = order_df["remaining"] - quantity_to_move_from_reserve
        order_df["quantity"] = quantity_to_move_from_reserve
        order_df["remaining"] = remaining_quantity
        return order_df

    def _deduct_qty(self, order_df, filtered_order):
        sell_quantity = min(order_df["quantity"], filtered_order["quantity"])
        sell_price = filtered_order["price"]
        order_df["quantity"] = order_df["quantity"] - sell_quantity
        filtered_order["quantity"] = filtered_order["quantity"] - sell_quantity

        if order_df["direction"] == "Sell":
            sell_order_id = order_df["id"]
            buy_order_id = filtered_order["id"]
        else:
            buy_order_id = order_df["id"]
            sell_order_id = filtered_order["id"]

        self.transaction_message.append(
            {
                "buyOrderId": buy_order_id,
                "sellOrderId": sell_order_id,
                "price": sell_price,
                "quantity": sell_quantity,
            }
        )
        return order_df, filtered_order

    def _fetch_matching_orders(self, order_df):
        if order_df["direction"].loc[0] == "Sell":
            price = order_df["price"].loc[0]
            users_query = f'SELECT * FROM orders_table WHERE orders_table.price >= {price} and orders_table.direction = "Buy" order by orders_table.price DESC, orders_table.timestamp'
            users_query_cleanup = f'DELETE FROM orders_table WHERE orders_table.price >= {price} and orders_table.direction = "Buy"'

        else:
            price = order_df["price"].loc[0]
            users_query = f'SELECT * FROM orders_table WHERE orders_table.price <= {price} and orders_table.direction = "Sell" order by orders_table.price ASC, orders_table.timestamp'
            users_query_cleanup = f'DELETE FROM orders_table WHERE orders_table.price <= {price} and orders_table.direction = "Sell"'

        with self.engine.connect() as conn:
            matching_orders = pd.read_sql_query(users_query, con=conn)
            conn.execute(users_query_cleanup)
        return matching_orders

    def fetch_current_state(self):
        """Gets current state of Sell & Buy orders in db.

        Returns:
            dataframe: sell/buy orders df
        """
        buy_orders_query = r'SELECT orders_table.id, orders_table.price, orders_table.quantity FROM orders_table WHERE orders_table.direction = "Buy" order by orders_table.price DESC, orders_table.timestamp'
        sell_orders_query = r'SELECT orders_table.id, orders_table.price, orders_table.quantity FROM orders_table WHERE orders_table.direction = "Sell" order by orders_table.price ASC, orders_table.timestamp'

        with self.engine.connect() as conn:
            buy_orders = pd.read_sql_query(buy_orders_query, con=conn)
            sell_orders = pd.read_sql_query(sell_orders_query, con=conn)
        return buy_orders, sell_orders


class OutputMaker:
    """Support class for output formating."""

    def print_prettifier(self, buy_orders, sell_orders):
        """Transforms dataframe data to required json format.

        Args:
            buy_orders (dataframe): buy orders df
            sell_orders (dataframe): sell orders df

        Returns:
            json: json to print to cmd.
        """
        state_json = {
            "buyOrders": buy_orders.to_dict("records"),
            "sellOrders": sell_orders.to_dict("records"),
        }
        return state_json


if __name__ == "__main__":
    order_book = OrdersHandler(BOOKING_DB_PATH)
    order_book.reset_table(BOOKING_DB_PATH)
    output_maker = OutputMaker()
    while True:
        cmd_filtered_order = input("Enter order JSON:")
        try:
            cmd_order_df = order_book.receive_order(cmd_filtered_order)
        except:
            print("Couldn't add order to existing order book.")
        try:
            cmd_buy_orders, cmd_sell_orders = order_book.fetch_current_state()
            cmd_state_json = output_maker.print_prettifier(
                cmd_buy_orders, cmd_sell_orders
            )
            print(cmd_state_json)
            print(order_book.transaction_message)
        except:
            print("Couldn't retreive data from order book.")
