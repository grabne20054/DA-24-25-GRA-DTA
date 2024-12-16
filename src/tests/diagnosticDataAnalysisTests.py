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

    assert result == (1.0, 1.0, 1.0)
    assert result[0] <= 1.0 and result[1] <= 1.0 and result[2] <= 1.0
    assert result[0] >= -1.0 and result[1] >= -1.0 and result[2] >= -1.0

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
                "productAmount": 10
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
            }
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    def mock_productNamebyId(self, product_id):
        if product_id == 1:
            return "Product1"
        elif product_id == 2:
            return "Product2"
        elif product_id == 3:
            return "Product3"
        elif product_id == 4:
            return "Product4"
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_productNamebyId)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(product_name="Product1")

    assert result == ["Product4", "Product3"]

def test05_performItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the perform method of ItemBoughtCorrelation class

    Test05:
    Data found, two products --> Not enough products to analyze (at least 3 products needed)
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
            {
                "productId": 2,
                "name": "Product2",
                "price": 200,
            },
            ]
    }

    def mock_collect(self):
        return pd.DataFrame(mock_data["orders"]), pd.DataFrame(mock_data["ordersProducts"]), pd.DataFrame(mock_data["products"])
    
    def mock_productNamebyId(self, product_id):
        if product_id == 1:
            return "Product1"
        elif product_id == 2:
            return "Product2"
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_productNamebyId)


    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis.perform("Product1")

    assert str(e.value) == "Not enough products to analyze"

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
    
    def mock_productNamebyId(self, product_id):
        if product_id == 1:
            return "Product1"
        elif product_id == 2:
            return "Product2"
        elif product_id == 3:
            return "Product3"
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_productNamebyId)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(product_name="Product1", combination_product_amount=3)

    assert result == ["Product3", "Product2"]

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
    
    def mock_productNamebyId(self, product_id):
        if product_id == 1:
            return "Product1"
        elif product_id == 2:
            return "Product2"
        elif product_id == 3:
            return "Product3"
        elif product_id == 4:
            return "Product4"
        elif product_id == 5:
            return "Product5"
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_productNamebyId)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(product_name="Product1", combination_product_amount=3)

    assert result == ["Product5", "Product4", "Product3"]

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
    
    def mock_productNamebyId(self, product_id):
        if product_id == 1:
            return "Product1"
        elif product_id == 2:
            return "Product2"
        elif product_id == 3:
            return "Product3"
        elif product_id == 4:
            return "Product4"
        elif product_id == 5:
            return "Product5"
        
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, 'collect', mock_collect)
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_productNamebyId)


    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis.perform(product_name="Product1", combination_product_amount=4)

    assert result == ["Product5", "Product4", "Product3", "Product2"]

def test09_getProductNameByIdItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the _getProductNameById method of ItemBoughtCorrelation class

    Test09:
    Product found
    '''

    mock_data = {
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
           
            ]
    }

    def mock_getProductNameById(self, product_id):
        return "Product1"
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_getProductNameById)

    analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
    result = analysis._getProductNameById(1)

    assert result == "Product1"

def test10_getProductNameByIdItemBoughtCorrelation(monkeypatch):
    '''
    Test case to check the _getProductNameById method of ItemBoughtCorrelation class

    Test10:
    Product not found
    '''

    mock_data = {
        "products":
        [
            {
                "productId": 1,
                "name": "Product1",
                "price": 100,
            },
           
            ]
    }

    def mock_getProductNameById(self, product_id):
        raise Exception("Product not found")
    
    monkeypatch.setattr(ItemBoughtCorrelation.ItemBoughtCorrelation, '_getProductNameById', mock_getProductNameById)

    with pytest.raises(Exception) as e:
        analysis = ItemBoughtCorrelation.ItemBoughtCorrelation()
        analysis._getProductNameById(2)

    assert str(e.value) == "Product not found"
