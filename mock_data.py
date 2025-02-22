import requests
from random import randint
import datetime

API_URL = "http://localhost:8002" # oder "http://185.243.187.210:8002"

def customerSignupMockData():

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
        year = str(randint(2022, datetime.datetime.now().year))
        month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
        day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
        customer["signedUp"] = f"{year}-{month}-{day}T19:49:40.433Z"
        if customer["signedUp"] <= datetime.datetime.now().isoformat():
            res = requests.post(API_URL +"/customers", json=customer)

        print(res.text)

def postManyOrders():
    order = {
            "orderDate": "2025-01-28T08:42:30.090Z",
            "deliveryDate": "2025-01-28T08:42:30.090Z",
            "customerReference": 0,
            "deleted": False,
            "orderState": "order_placed",
            "selfCollect": True,
    }

    for i in range(0, 999):
        order["customerReference"] = randint(0, 400)	
        year = str(randint(2019, datetime.datetime.now().year - 1))
        month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
        day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
        order["orderDate"] = f"{year}-{month}-{day}T19:49:40.433Z"
        res = requests.post(API_URL +"/orders", json=order)

        print(res.text)


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

def postManyProductOrders():
    orders = requests.get(API_URL +"/orders")
    products = requests.get(API_URL +"/products")

    orders = orders.json()
    products = products.json()

    counter = 0

    for order in orders:
        order_id = order["orderId"]
        for product in products:
            counter += 1
            product_id = product["productId"]
            year = str(randint(2019, datetime.datetime.now().year - 1))
            month = str(randint(1, 12)).zfill(2)  # Zero-padding for month
            day = str(randint(1, 28)).zfill(2)    # Zero-padding for day
            orderDate = f"{year}-{month}-{day}T19:49:40.433Z"
            res = requests.post(API_URL +f"/ordersProducts/{order_id}/{product_id}/{randint(1,20)}/{orderDate}")
            print(res.text)
        if counter == 10:
            break

def postManyRoutes():
    for i in range(0, 100):
        route = {
            "name": f"Stubenberg {i}",
            "deleted": False,
        }

        res = requests.post(API_URL +"/routes/", json=route)
        print(res.text)

def postRoutesOrders():
    routes = requests.get(API_URL +"/routes")
    orders = requests.get(API_URL +"/orders")

    routes = routes.json()
    orders = orders.json()

    counter = 0
    for order in orders:
        order_id = order["orderId"]
        for route in routes:
            route_id = route["routeId"]
            if route["name"] == "string":
                continue
            res = requests.post(API_URL +f"/routesOrders/{route_id}/{order_id}")
            counter += 1
            print(res.text)
        if counter == 10:
            break
            

if __name__ == "__main__":
    customerSignupMockData() #1
    postManyProducts() #2
    postManyOrders() #3
    postManyProductOrders() #4
    postManyRoutes() #5
    postRoutesOrders() #6