ORDERS_SAMPLE_TEST_JSON = {
    "sample_case1": {
      "reset": True,
      "input": "{\"type\": \"Limit\", \"order\": {\"direction\": \"Buy\", \"id\": 1, \"price\": 14, \"quantity\": 20}}",
      "state": "{\"buyOrders\": [{\"id\": 1, \"price\": 14, \"quantity\": 20}], \"sellOrders\": []}",
      "transactions": "[]"
    },
    "sample_case2": {
      "reset": False,
      "input": "{\"type\": \"Iceberg\", \"order\": {\"direction\": \"Buy\", \"id\": 2, \"price\": 15, \"quantity\": 50,\"peak\": 20}}",
      "state": "{\"buyOrders\": [{\"id\": 2, \"price\": 15, \"quantity\": 20}, {\"id\": 1, \"price\": 14,\"quantity\": 20}], \"sellOrders\": []}",
      "transactions": "[]"
    },
    "sample_case3": {
      "reset": False,
      "input": "{\"type\": \"Limit\", \"order\": {\"direction\": \"Sell\", \"id\": 3, \"price\": 16, \"quantity\": 15}}",
      "state": "{\"buyOrders\": [{\"id\": 2, \"price\": 15, \"quantity\": 20}, {\"id\": 1, \"price\": 14, \"quantity\": 20}],\"sellOrders\": [{\"id\": 3, \"price\": 16, \"quantity\": 15}]}",
      "transactions": "[]"
    },
    "sample_case4": {
      "reset": False,
      "input": "{\"type\": \"Limit\", \"order\": {\"direction\": \"Sell\", \"id\": 4, \"price\": 13, \"quantity\": 60}}",
      "state": "{\"buyOrders\": [{\"id\": 1, \"price\": 14, \"quantity\": 10}], \"sellOrders\": [{\"id\": 3, \"price\": 16,\"quantity\": 15}]}",
      "transactions": "[{\"buyOrderId\": 2, \"sellOrderId\": 4, \"price\": 15, \"quantity\": 20}, {\"buyOrderId\": 2, \"sellOrderId\": 4, \"price\": 15, \"quantity\": 20}, {\"buyOrderId\": 2, \"sellOrderId\": 4, \"price\": 15, \"quantity\": 10}, {\"buyOrderId\": 1, \"sellOrderId\": 4, \"price\": 14, \"quantity\": 10}]"
    }
  }

ORDERS_VERIFY_TEST_JSON = {
    "verify_case1": {
      "reset": True,
      "final": False,
      "input": "{\"type\": \"Iceberg\", \"order\": {\"direction\": \"Sell\", \"id\": 1, \"price\": 100, \"quantity\": 200, \"peak\": 100}}",
      "state": "{}",
      "transactions": "[]"
    },
    "verify_case2": {
      "reset": False,
      "final": False,
      "input": "{\"type\": \"Iceberg\", \"order\": {\"direction\": \"Sell\", \"id\": 2, \"price\": 100, \"quantity\": 300, \"peak\": 100}}",
      "state": "{}",
      "transactions": "[]"
    },
    "verify_case3": {
      "reset": False,
      "final": False,
      "input": "{\"type\": \"Iceberg\", \"order\": {\"direction\": \"Sell\", \"id\": 3, \"price\": 100, \"quantity\": 200, \"peak\": 100}}",
      "state": "{}",
      "transactions": "[]"
    },
    "verify_case4": {
      "reset": False,
      "final": True,
      "input": "{\"type\": \"Iceberg\", \"order\": {\"direction\": \"Buy\", \"id\": 4, \"price\": 100, \"quantity\": 500, \"peak\": 100}}",
      "state": "{ \"buyOrders\": [], \"sellOrders\": [{\"id\": 2, \"price\": 100, \"quantity\": 100}, {\"id\": 3, \"price\": 100, \"quantity\": 100}]}",
      "transactions": "[]"
    }
  }