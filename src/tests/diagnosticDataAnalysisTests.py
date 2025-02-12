import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd

from DataAnalysis.diagnostic import ProductOrdersCorrelation, ItemBoughtCorrelation

def test01_performProductOrdersCorrelationNoData(monkeypatch):
    '''
    Test case to check the perform method of ProductOrdersCorrelation class with no data

    Test01:
    No data
    '''

    def mock_collect(self):
        return None, None, None, None
    
    monkeypatch.setattr(ProductOrdersCorrelation.ProductOrdersCorrelation, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ProductOrdersCorrelation.ProductOrdersCorrelation()
        analysis.perform()

    assert str(e.value) == "No data found"

def test02_performProductOrdersCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ProductOrdersCorrelation class

    Test02:
    Data found

    Note that the correlation values are 1.0 because the data is generated in such a way that the correlation between productAmount and price, orderDate, businessSector is 1.0
    This can be simple achieved by working with two entities each.
    Therefore it gets checked if the correlation values are between -1.0 and 1.0
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            },
            {
                "orderId": 2,
                "orderDate": "2021-02-02",
                "deliveryDate": "2021-01-03",
                "customerReference": 2,	
            },
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 2,
                "productId": 2,
                "productAmount": 20,
            },
        ]
        ,
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
        ]
        ,
        "customers":
        [
            {
                "customerId": 1,
                "firstname": "Customer1",
                "lastname": "Customer1",
                "email": "test@gmail.com",
                "customerReference": 1,
                "password": "password",
                "phoneNumber": "1234567890",
                "companyNumber": "1234567890",
                "signedUp": "2021-01-01",
                "role": "Admin",
                "businessSector": "Sector1",
                "addressId": 1,
            },
            {
                "customerId": 2,
                "firstname": "Customer2",
                "lastname": "Customer2",
                "email": "test@gmail.com",
                "customerReference": 2,
                "password": "password",
                "phoneNumber": "1234567890",
                "companyNumber": "1234567890",
                "signedUp": "2021-01-01",	
                "role": "Admin",
                "businessSector": "Sector2",
                "addressId": 2,
            },
        ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"]), pd.DataFrame(mock_data["customers"])

    monkeypatch.setattr(ProductOrdersCorrelation.ProductOrdersCorrelation, 'collect', mock_collect)

    analysis = ProductOrdersCorrelation.ProductOrdersCorrelation()
    result = analysis.perform()

    assert result == {'product-price-corr' : 1.0, 'product-orderDate-corr' : 1.0, 'product-businessSector-corr' : 1.0, "lower-bound": -1, "upper-bound": 1, "typeofgraph": "gauge"}
    assert result["product-price-corr"] >= -1 and result["product-price-corr"] <= 1
    assert result["product-orderDate-corr"] >= -1 and result["product-orderDate-corr"] <= 1
    assert result["product-businessSector-corr"] >= -1 and result["product-businessSector-corr"] <= 1

def test03_performItemBoughtCorrelationNoData(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class with no data

    Test03:
    No data
    '''

    def mock_collect(self):
        return None, None, None
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform("test product")

    assert str(e.value) == "No data found"

def test04_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test04:
    Data found, four products
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10,
            }


        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            {
                "productId": 4,
                "name": "Product4",
                "price": 400,
            }
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(1)

    assert result == {"products": [2, 4]}

def test05_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test05:
    Data found, two products --> Not enough products to analyze (at least 2 products needed)
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)


    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(1)

    assert str(e.value) == "Too many products to combine"

def test06_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test06:
    Data found, three products, combination_product_amount = 3 -> returns all products in this case 2
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(1)

    assert result == {"products": [2, 3]}

def test07_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test07:
    Data found, five products, combination_product_amount = 3 -> should return 3 products
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 5,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            {
                "productId": 4,
                "name": "Product4",
                "price": 400,
            },
            {
                "productId": 5,
                "name": "Product5",
                "price": 500,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(1, combination_product_amount=3)

    assert result == {"products": [4, 2, 3]}

def test08_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class
    
    Test08:
    Data found, five products, combination_product_amount = 4 -> should return 4 products
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 5,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 4,
                "productAmount": 10
            }
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            {
                "productId": 4,
                "name": "Product4",
                "price": 400,
            },
            {
                "productId": 5,
                "name": "Product5",
                "price": 500,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(1, combination_product_amount=4)

    assert result == {"products": [4, 2, 3, 5]}


def test09_performItemBoughtCorrelationProductNotFound(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test09:
    Product not found
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(4)

    assert str(e.value) == "Product not found"

def test10_performItemBoughtCorrelationProductsToCombineNegative(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class
    
    Test10:
    combination_product_amount < 1
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)

    with pytest.raises(ValueError) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(1, combination_product_amount=-1)

    assert str(e.value) == "Not enough products to combine"

def test11_performItemBoughtCorrelationEmptyDataframes(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test11:
    Empty dataframes
    '''

    mock_data = {
        "orders": [],
        "ordersProducts": [],
        "products": []
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(1)

    assert str(e.value) == "One or more dataframes are empty"

def test12_performItemBoughtCorrelationErrorInMergingDataframes(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class
    
    Test12:
    Error in merging dataframes
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    def mock_merge(self, df_orders, df_ordersProducts, df_products):
        raise Exception("Error in merging dataframes")
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(pd, 'merge', mock_merge)

    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(1)

    assert str(e.value) == "Error in merging dataframes"

def test13_performItemBoughtCorrelationTooManyProductsToCombine(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test13:
    Too many products to combine
    '''

    mock_data = {
        "orders":
        [
            {
                "orderId": 1,
                "orderDate": "2021-01-01",
                "deliveryDate": "2021-01-02",
                "customerReference": 1,	
            }
            ]
        ,
        "ordersProducts":
        [
            {
                "orderId": 1,
                "productId": 1,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 2,
                "productAmount": 10,
            },
            {
                "orderId": 1,
                "productId": 3,
                "productAmount": 10,
            },
        ],
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            {
                "productId": 3,
                "name": "Product3",
                "price": 300,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)

    with pytest.raises(ValueError) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform(1, combination_product_amount=4)

    assert str(e.value) == "Too many products to combine"
