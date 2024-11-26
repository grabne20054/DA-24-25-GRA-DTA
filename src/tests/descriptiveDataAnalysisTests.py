import pytest
import os,sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DataAnalysis.descriptive import CustomerSignup, EmployeeAmount, ProductsAmount, ProductsMostlyBought, RoutesAmount
from DataAnalysis.APIDataHandler import APIDataHandler

###################### CustomerSignup Class ######################

def test01_performCustomerSignupNoData(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with no data

    Test01:
    No data
    '''
    def mock_collect(self):
        return None
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = CustomerSignup.CustomerSignup()
        CustomerSignup.CustomerSignup.perform(analysis, 0, False, False)

    assert str(e.value) == "No data found"

def test02_performCustomerSignupLastDays(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with last_days parameter

    Test02:
    last_days = 0
    '''
    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 0, False, False)

    assert result == {'growth': {'2021-01-01': 1, '2021-01-02': 1, '2021-01-03': 1, '2021-01-04': 1}, 'cumulative_growth': {'2021-01-01': 1, '2021-01-02': 2, '2021-01-03': 3, '2021-01-04': 4}}

def test03_performCustomerSignupLastDays(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with last_days parameter
    Should return the growth for the last day -> in this case nothing

    Test03:
    last_days = 1
    '''
    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 1, False, False)

    assert result == {'growth': {}, 'cumulative_growth': {}}

def test04_performCustomerSignupLastDays(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with last_days parameter
    Should return the growth for the last 2 days

    Test04:
    last_days = 2
    '''
    mock_data = [
        {
            "signedUp": datetime.now().strftime("%Y-%m-%dt%H:%M:%S.%f") 
        },
        {
            "signedUp": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dt%H:%M:%S.%f")
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 2, False, False)

    yesterday = datetime.now() - timedelta(days=1)

    assert result == {'growth': {str(datetime.now().strftime("%Y-%m-%d")): 1, yesterday.strftime("%Y-%m-%d"): 1}, 'cumulative_growth': {yesterday.strftime("%Y-%m-%d"): 1, str(datetime.now().strftime("%Y-%m-%d")) : 2 }}

def test05_performCustomerSignupYearlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with yearly growth

    Test05:
    yearly growth = True
    '''

    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 0, True, False)

    assert result == {'growth': {'2021': 4}, 'cumulative_growth': {'2021': 4}}

def test06_performCustomerSignupMonthlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with monthly growth

    Test06:
    monthly growth = True
    '''

    mock_data = [
        {
            "signedUp": datetime.now().strftime("%Y-%m-%dt%H:%M:%S.%f")
        },
        {
            "signedUp": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dt%H:%M:%S.%f") 
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 0, False, True)

    assert result == {'growth': {'11': 2}, 'cumulative_growth': {'11': 2}}

def test07_performCustomerSignupYearlyGrowthTrueMonthlyGrowthTrue(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with yearly growth = True and monthly growth = True
    Should only return the yearly growth

    Test08:
    yearly growth = True
    monthly growth = True
    '''

    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 0, True, True)

    assert result == {'growth': {'2021': 4}, 'cumulative_growth': {'2021': 4}}

def test08_performCustomerSignupYearlyGrowthTrueMonthlyGrowthTrueLastDays(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with yearly growth = True, monthly growth = True and last_days = 2
    Should only return the yearly growth

    Test08:
    yearly growth = True
    monthly growth = True
    last_days = 2
    '''

    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()
    result = CustomerSignup.CustomerSignup.perform(analysis, 2, True, True)

    assert result == {'growth': {'2021': 4}, 'cumulative_growth': {'2021': 4}}

def test09_performCustomerSignupLastDaysNegative(monkeypatch):
    '''
    Test case to check the perform method of CustomerSignup class with last_days parameter negative
    Should raise ValueError

    Test09:
    last_days = -1
    '''
    mock_data = [
        {
            "signedUp": "2021-01-01t00:00:00.000"
        },
        {
            "signedUp": "2021-01-02t00:00:00.000"
        },
        {
            "signedUp": "2021-01-03t00:00:00.000"
        },
        {
            "signedUp": "2021-01-04t00:00:00.000"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(CustomerSignup.CustomerSignup, 'collect', mock_collect)

    analysis = CustomerSignup.CustomerSignup()

    with pytest.raises(ValueError) as e:
        CustomerSignup.CustomerSignup.perform(analysis, -1, False, False)

    assert str(e.value) == "The number of days should be greater than zero"

###################### Employee Amount Class ######################

def test10_performEmployeeAmountNoData(monkeypatch):
    '''
    Test case to check the perform method of EmployeeAmount class with no data

    Test10:
    No data
    '''
    def mock_collect(self):
        return None
    
    monkeypatch.setattr(EmployeeAmount.EmployeeAmount, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = EmployeeAmount.EmployeeAmount()
        EmployeeAmount.EmployeeAmount.perform(analysis)

    assert str(e.value) == "No data found"

def test11_performEmployeeAmount(monkeypatch):
    '''
    Test case to check the perform method of EmployeeAmount class

    Test11:
    Data available
    '''
    mock_data = [
        {
            "role": "admin"
        },
        {
            "role": "admin"
        },
        {
            "role": "admin"
        },
        {
            "role": "employee"
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(EmployeeAmount.EmployeeAmount, 'collect', mock_collect)

    analysis = EmployeeAmount.EmployeeAmount()
    result = EmployeeAmount.EmployeeAmount.perform(analysis)

    assert result == {'admin': 3, 'employee': 1}

###################### Products Amount Class ######################

def test12_performProductsAmountNoData(monkeypatch):
    '''
    Test case to check the perform method of ProductsAmount class with no data

    Test12:
    No data
    '''
    def mock_collect(self):
        return None
    
    monkeypatch.setattr(ProductsAmount.ProductsAmount, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ProductsAmount.ProductsAmount()
        ProductsAmount.ProductsAmount.perform(analysis)

    assert str(e.value) == "No data found"

def test13_performProductsAmount(monkeypatch):
    '''
    Test case to check the perform method of ProductsAmount class

    Test13:
    Data available
    '''
    mock_data = [
        {
            "name": "product1",
            "stock": 5
        },
        {
            "name": "product2",
            "stock": 10
        },
        {
            "name": "product3",
            "stock": 15
        },
        {
            "name": "product4",
            "stock": 20
        }
    ]

    def mock_collect(self):
        return mock_data
    
    monkeypatch.setattr(ProductsAmount.ProductsAmount, 'collect', mock_collect)

    analysis = ProductsAmount.ProductsAmount()
    result = ProductsAmount.ProductsAmount.perform(analysis)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

###################### Products Mostly Bought Class ######################

def test14_performProductsMostlyBoughtNoData(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with no data

    Test14:
    No data
    '''
    def mock_collect(self):
        return None
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = ProductsMostlyBought.ProductsMostlyBought()
        ProductsMostlyBought.ProductsMostlyBought.perform(analysis)

    assert str(e.value) == "No data found"

def test15_performProductsMostlyBought(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class

    Test15:
    Data available
    '''
    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, oder_id):
        return "2021-01-01"
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test16_performProductsMostlyBoughtNoProductFound(monkeypatch):

    '''
    Test case to check the perform method of ProductsMostlyBought class
    Should raise Exception if product not found

    Test16:
    Product not found
    '''

    mock_data_collect = [
        {
            "productId": None,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": None,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": None,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": None,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getOrderDate(self, oder_id):
        return "2021-01-01"
    
    def mock_getProductNameById(self, product_id):
        raise Exception("Product not found")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()

    with pytest.raises(Exception) as e:
        ProductsMostlyBought.ProductsMostlyBought.perform(analysis)

    assert str(e.value) == "Product not found"

def test17_performProductsMostlyBoughtNoOrderFound(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class
    Should raise Exception if order not found

    Test17:
    Order not found
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": None,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": None,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": None,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": None,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        raise Exception("Order not found")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()

    with pytest.raises(Exception) as e:
        ProductsMostlyBought.ProductsMostlyBought.perform(analysis, last_days=1)

    assert str(e.value) == "Order not found"

def test18_performProductsMostlyBoughtLastDays(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with last_days parameter

    Test18:
    last_days = 2
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, last_days=1)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test19_performProductsMostlyBoughtLastDays(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with last_days parameter
    Should only return the products bought in the last 2 days

    Test19:
    last_days = 2
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        if order_id == 28:
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 2:
            return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 10:
            return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 20:
            return (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, last_days=2)

    assert result == {'product1': 5, 'product2': 10}

def test20_performProductsMostlyBoughtLastDays(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with last_days parameter
    Should only return the products bought in the last day
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        if order_id == 28:
            return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 2:
            return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 10:
            return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 20:
            return (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, last_days=1)

    assert result == {}

def test21_performProductsMostlyBoughtLastDaysNegative(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with last_days parameter negative
    Should raise ValueError

    Test21:
    last_days = -1
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()

    with pytest.raises(ValueError) as e:
        ProductsMostlyBought.ProductsMostlyBought.perform(analysis, last_days=-1)

    assert str(e.value) == "The number of days should be greater than zero"

def test22_performProductsMostlyBoughtYearlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with yearly growth

    Test22:
    Yearly Growth True
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=True, month=False)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test23_performProductsMostlyBoughtYearlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with yearly growth
    Should only return the yearly growth

    Test23:
    Yearly Growth True
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return '2021-01-01T00:00:00.000'
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=True, month=False)

    assert result == {}
    
    



    ## Yearly Growth True, Monthly Growth True

def test24_performProductsMostlyBoughtMonthlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with monthly growth

    Test24:
    Monthly Growth True
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=False, month=True)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test25_performProductsMostlyBoughtMonthlyGrowth(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with monthly growth
    Should only return the monthly growth

    Test25:
    Monthly Growth True
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return '2024-10-01T00:00:00.000'
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=False, month=True)

    assert result == {}

def test26_performProductsMostlyBoughtYearlyGrowthTrueMonthlyGrowthTrue(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with yearly
    growth = True and monthly growth = True
    Should only return the yearly growth

    Test26:
    Yearly Growth True
    Monthly Growth True
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return '2024-01-01T00:00:00.000'
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=True, month=True)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test27_performProductsMostlyBoughtYearlyGrowthTrueMonthlyGrowthTrueLastDays(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with yearly
    growth = True, monthly growth = True and last_days = 2
    Should only return the yearly growth


    Test27:
    Yearly Growth True
    Monthly Growth True
    Last Days = 2
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        return '2024-01-01T00:00:00.000'
    
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=True, month=True, last_days=2)

    assert result == {'product1': 5, 'product2': 10, 'product3': 15, 'product4': 20}

def test28_performProductsMostlyBoughtYearlyGrowthFalseMonthlyGrowthTrueLastDays(monkeypatch):
    '''
    Test case to check the perform method of ProductsMostlyBought class with yearly
    growth = False, monthly growth = True and last_days = 2
    Should only return the monthly growth

    Test28:
    Yearly Growth False
    Monthly Growth True
    Last Days = 2
    '''

    mock_data_collect = [
        {
            "productId": 1,
            "orderId": 28,
            "productAmount": 5
        },
        {
            "productId": 2,
            "orderId": 2,
            "productAmount": 10
        },
        {
            "productId": 3,
            "orderId": 10,
            "productAmount": 15
        },
        {
            "productId": 4,
            "orderId": 20,
            "productAmount": 20
        }
    ]

    def mock_collect(self):
        return mock_data_collect
    
    def mock_getProductNameById(self, product_id):
        return "product" + str(product_id)
    
    def mock_getOrderDate(self, order_id):
        if order_id == 28:
            return (datetime.now() - timedelta(weeks=5)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 2:
            return (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 10:
            return (datetime.now() - timedelta(weeks=3)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif order_id == 20:
            return (datetime.now() - timedelta(weeks=4)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, 'collect', mock_collect)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getProductNameById', mock_getProductNameById)
    monkeypatch.setattr(ProductsMostlyBought.ProductsMostlyBought, '_getOrderDate', mock_getOrderDate)

    analysis = ProductsMostlyBought.ProductsMostlyBought()
    result = ProductsMostlyBought.ProductsMostlyBought.perform(analysis, year=False, month=True, last_days=2)

    assert result == {'product2': 10, 'product3': 15}

###################### Routes Amount Class ######################
    
def test29_performRoutesAmountNoData(monkeypatch):
    '''
    Test case to check the perform method of RoutesAmount class with no data

    Test29:
    No data
    '''
    def mock_collect(self):
        return None
    
    monkeypatch.setattr(RoutesAmount.RoutesAmount, 'collect', mock_collect)

    with pytest.raises(Exception) as e:
        analysis = RoutesAmount.RoutesAmount()
        RoutesAmount.RoutesAmount.perform(analysis)

    assert str(e.value) == "No data found"

def test30_performRoutesAmountData(monkeypatch):
    '''
    Test case to check the perform method of RoutesAmount class

    Test30:
    Data available
    '''

    mock_data = [
        {
            "routeId": 1,
            "orderId": 1
        },
        {
            "routeId": 2,
            "orderId": 2
        },
        {
            "routeId": 3,
            "orderId": 3
        },
        {
            "routeId": 4,
            "orderId": 4
        }
    ]

    def mock_collect(self):
        return mock_data
    
    def mock_getRouteNameById(self, route_id):
        return "route" + str(route_id)
    
    monkeypatch.setattr(RoutesAmount.RoutesAmount, 'collect', mock_collect)
    monkeypatch.setattr(RoutesAmount.RoutesAmount, '_getRouteNameById', mock_getRouteNameById)

    analysis = RoutesAmount.RoutesAmount()
    result = RoutesAmount.RoutesAmount.perform(analysis)

    assert result == {'route1': 1, 'route2': 1, 'route3': 1, 'route4': 1}

def test31_performRoutesAmountDataMultipleData(monkeypatch):
    '''
    Test case to check the perform method of RoutesAmount class with multiple data
    
    Test31:
    Multiple data
    '''

    mock_data = [
        {
            "routeId": 1,
            "orderId": 1
        },
        {
            "routeId": 2,
            "orderId": 2
        },
        {
            "routeId": 3,
            "orderId": 3
        },
        {
            "routeId": 4,
            "orderId": 4
        },
        {
            "routeId": 1,
            "orderId": 5
        },
        {
            "routeId": 2,
            "orderId": 6
        },
        {
            "routeId": 3,
            "orderId": 7
        },
        {
            "routeId": 4,
            "orderId": 8
        }
    ]

    def mock_collect(self):
        return mock_data
    
    def mock_getRouteNameById(self, route_id):
        return "route" + str(route_id)
    
    monkeypatch.setattr(RoutesAmount.RoutesAmount, 'collect', mock_collect)
    monkeypatch.setattr(RoutesAmount.RoutesAmount, '_getRouteNameById', mock_getRouteNameById)

    analysis = RoutesAmount.RoutesAmount()
    result = RoutesAmount.RoutesAmount.perform(analysis)

    assert result == {'route1': 2, 'route2': 2, 'route3': 2, 'route4': 2}

def test32_performRoutesAmountRouteNotFound(monkeypatch):
    '''
    Test case to check the perform method of RoutesAmount class
    Should raise Exception if route not found

    Test32:
    Route not found
    '''

    mock_data = [
        {
            "routeId": None,
            "orderId": 1
        },
        {
            "routeId": None,
            "orderId": 2
        },
        {
            "routeId": None,
            "orderId": 3
        },
        {
            "routeId": None,
            "orderId": 4
        }
    ]

    def mock_collect(self):
        return mock_data
    
    def mock_getRouteNameById(self, route_id):
        raise Exception("Route not found")
    
    monkeypatch.setattr(RoutesAmount.RoutesAmount, 'collect', mock_collect)
    monkeypatch.setattr(RoutesAmount.RoutesAmount, '_getRouteNameById', mock_getRouteNameById)

    analysis = RoutesAmount.RoutesAmount()

    with pytest.raises(Exception) as e:
        RoutesAmount.RoutesAmount.perform(analysis)

    assert str(e.value) == "Route not found"

