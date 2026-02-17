import requests
from random import randint
import datetime
from time import sleep

API_URL = "http://185.243.187.210:8002" # oder "http://185.243.187.210:8002"

def postAdressMockData():
    address = {
        "streetName": "string",
        "streetNumber": "string",
        "city": "string",
        "postCode": "string",
        "country": "string",
        "state": "string",
        "modifiedAt": "2025-02-22T12:43:40.199Z",
        "deleted": True
        }

    for i in range(0, 100):
        address["streetName"] = "streetName" + str(i)
        address["streetNumber"] = "streetNumber" + str(i)
        address["city"] = "city" + str(i)
        address["postCode"] = "postCode" + str(i)
        address["country"] = "country" + str(i)
        address["state"] = "state" + str(i)
        address["modifiedAt"] = "2025-02-22T12:43:40.199Z"
        address["deleted"] = False
        res = requests.post(API_URL +"/addresses", json=address)

        print(res.text)
    sleep(2)

def customerSignupMockData():

    adresses = requests.get(API_URL +"/addresses")
    if adresses.status_code == 200:
        adresses = adresses.json()
    else:
        print(f"Failed to fetch addresses: {adresses.status_code}")
        return


    customer = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "email",
        "customerReference": 0,
        "password": "password",
        "phoneNumber": "phoneNumber",
        "companyNumber": "companyName",
        "signedUp": "2024-11-11T19:49:40.433Z",
        "role": "admin",
        "businessSector": "it",
        "addressId": "a79d8e22-0ff2-42b9-9af8-61935f39e35e",
        "deleted": False,
        "avatarPath": "string",
        "modifiedAt": "2024-11-11T19:49:40.433Z"
    }

    for i in range(0, 101):
        customer["firstname"] = "John" + str(i)
        customer["lastname"] = "Doe" + str(i)
        customer["email"] = "email" + str(i)
        customer["customerReference"] = int(i)
        customer["phoneNumber"] = "phoneNumber" + str(i)
        customer["companyNumber"] = "companyName" + str(i)
        customer["businessSector"] = ["tourism", "it", "agriculture"][randint(0, 2)]
        customer["addressId"] = adresses[randint(0, len(adresses) - 1)]["addressId"]
        year = str(randint(2022, datetime.datetime.now().year))
        month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
        day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
        customer["signedUp"] = f"{year}-{month}-{day}T19:49:40.433Z"
        res = requests.post(API_URL +"/customers", json=customer)

        print(res.text)
    sleep(2)

def postManyOrders():
    order = {
            "orderDate": "2025-01-28T08:42:30.090Z",
            "deliveryDate": "2025-01-28T08:42:30.090Z",
            "customerReference": 0,
            "deleted": False,
            "orderState": "order_placed",
            "selfCollect": True,
    }

    for i in range(0, 100):
        order["customerReference"] = randint(0, 100)	
        year = str(randint(2019, datetime.datetime.now().year - 1))
        month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
        day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
        order["orderDate"] = f"{year}-{month}-{day}T19:49:40.433Z"
        res = requests.post(API_URL +"/orders", json=order)

        print(res.text)
    sleep(2)


def postManyProducts():
    for i in range(0, 200):
        product = {
            "name": f"product{i}",
            "description": f"description{i}",
            "price": randint(1, 100),
            "stock": randint(1, 100),
            "imagePath": f"imagePath{i}",
            "deleted": False,
            "modifiedAt": None,
            "createdAt": datetime.datetime.now().isoformat()
        }

        res = requests.post(API_URL +"/products/", json=product)
        print(res.text)
    sleep(2)

def postManyProductOrders():
    orders = requests.get(API_URL +"/orders")
    products = requests.get(API_URL +"/products")

    if orders.status_code != 200 or products.status_code != 200:
        print("Failed to fetch orders or products")
        return

    orders = orders.json()
    products = products.json()

    for _ in range(200):
        order = orders[randint(0, len(orders) - 1)]
        product = products[randint(0, len(products) - 1)]
        order_id = order["orderId"]
        product_id = product["productId"]
        year = str(randint(2019, datetime.datetime.now().year - 1))
        month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
        day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
        orderDate = f"{year}-{month}-{day}T19:49:40.433Z"
        res = requests.post(API_URL +f"/ordersProducts/{order_id}/{product_id}/{randint(1,20)}/{orderDate}")
        print(res.text)

    sleep(2)

def postManyRoutes():
    for i in range(0, 100):
        route = {
            "name": f"Stubenberg {i}",
            "deleted": False,
        }

        res = requests.post(API_URL +"/routes/", json=route)
        print(res.text)
    sleep(2)

def postRoutesOrders():
    routes = requests.get(API_URL +"/routes")
    orders = requests.get(API_URL +"/orders")

    if routes.status_code != 200 or orders.status_code != 200:
        print("Failed to fetch routes or orders")
        return

    routes = routes.json()
    orders = orders.json()

    for _ in range(100):
        route = routes[randint(0, len(routes) - 1)]
        order = orders[randint(0, len(orders) - 1)]
        route_id = route["routeId"]
        order_id = order["orderId"]
        res = requests.post(API_URL +f"/routesOrders/{route_id}/{order_id}")
        print(res.text)
    sleep(2)
            

def postManyEmployees():
    for i in range(0, 100):
        employee = {
            "firstName": f"firstName{i}",
            "lastName": f"lastName{i}",
            "password": f"password{i}",
            "email": f"email{i}",
            "role": "admin",
            "deleted": False
        }

        employee["role"] = ["admin", "employee", "supplier"][randint(0, 2)]

        res = requests.post(API_URL +"/employess", json=employee)
        print(res.text)
        print(res)
    sleep(2)


if __name__ == "__main__":
    postManyEmployees()
    """postAdressMockData() #0
    customerSignupMockData() #1
    postManyProducts() #2
    postManyOrders() #3
    postManyProductOrders() #4
    postManyRoutes() #5
    postRoutesOrders() #6"""