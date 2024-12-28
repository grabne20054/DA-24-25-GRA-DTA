from enum import Enum

class REMOVINGS(Enum):
    """
    Enum class for removing values
    
    if the key is part of the enum and the correlating value is None , whole data set will be removed
    if the key is part of the enum and the correlating value is an empty string, whole data set will be removed
    """
    SIGNEDUP = 'signedUp'
    DELIVERYDATE = 'deliveryDate'
    DATE = 'date'
    PAYMENTDATE = 'paymentDate'
    CITY = 'city'
    COUNTRY = 'country'
    STATE = 'state'
    POSTCODE = 'postcode'
    NAME = 'name'
    AMOUNT = 'amount'
    PRICE = 'price'
    INVOICEAMOUNT = 'invoiceAmount'
    PRODUCTAMOUNT = 'productAmount'
    ROLE = 'role'
    BUSINESSSECTOR = 'businessSector'
    CUSTOMERID = 'customerId'
    ADDRESSID = 'addressId'
    ORDERID = 'orderId'
    PRODUCTID = 'productId'
    INVOICEID = 'invoiceId'
    EMPLOYEEID = 'employeeId'
    CONFIGID = 'configId'
    CARTID = 'cartId'
    CATEGORYID = 'categoryId'
    ROUTEID = 'routeId'

