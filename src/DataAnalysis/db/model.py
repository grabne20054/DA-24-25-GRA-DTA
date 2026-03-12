from sqlalchemy import Integer, String, ForeignKey, DateTime, Table, Column, Boolean, UUID
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from datetime import datetime
from typing import List
from enum import Enum as pyenum
import uuid

Base = declarative_base()

    
class Sector(str, pyenum):
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    EDUCATION = "education"
    FINANCE = "finance"
    HEALTH = "health"
    HOSPITALITY = "hospitality"
    IT = "it"
    MANUFACTURING = "manufacturing"
    OTHER = "other"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    TOURISM = "tourism"
    TRANSPORTATION = "transportation"

class OrderState(str, pyenum):
    ORDER_PLACED = "order_placed"
    ORDER_COLLECTED = "order_collected"
    IN_PROGRESS = "in_progress"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"

categoriesProducts = Table(
    "categoriesProducts",
    Base.metadata,
    Column("categoryId", UUID, ForeignKey("categories.categoryId")),
    Column("productId", UUID, ForeignKey("products.productId")),
)

cartsProducts = Table(
    "cartsProducts",
    Base.metadata,
    Column("cartId", UUID, ForeignKey("carts.cartId")),
    Column("productId", UUID, ForeignKey("products.productId")),
    Column("productAmount", Integer, nullable=False, default=1),
)

ordersProducts = Table(
    "ordersProducts",
    Base.metadata,
    Column("orderId", UUID, ForeignKey("orders.orderId")),
    Column("productId", UUID, ForeignKey("products.productId")),
    Column("productAmount", Integer, nullable=False, default=1),
    Column("orderDate", DateTime, nullable=False, default=datetime.now()),
)

routesOrders = Table(
    "routesOrders",
    Base.metadata,
    Column("routeId", UUID, ForeignKey("routes.routeId")),
    Column("orderId", UUID, ForeignKey("orders.orderId")),
)

class Employee(Base):
    __tablename__ = "employees"

    employeeId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    #firstName: Mapped[str] = mapped_column(String(255),nullable=False)
    #lastName: Mapped[str] = mapped_column(String(255),nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    roleId: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)



class SiteConfig(Base):
    __tablename__ = "siteConfigs"

    siteConfigId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    companyName: Mapped[str] = mapped_column(String(255), nullable=False)
    logoPath: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phoneNumber: Mapped[str] = mapped_column(String(15), nullable=False)
    companyNumber: Mapped[str] = mapped_column(String(255), nullable=True)
    iban: Mapped[str] = mapped_column(String(40), nullable=False)
    addressId: Mapped[int] = mapped_column(ForeignKey("addresses.addressId"), nullable=False)

    modifiedAt: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    address: Mapped["Address"] = relationship("Address", back_populates="siteConfig")

class Address(Base):
    __tablename__ = "addresses"

    addressId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    streetName: Mapped[str] = mapped_column(String(255), nullable=False)
    streetNumber: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postCode: Mapped[str] = mapped_column(String(10), nullable=False)
    country: Mapped[str] = mapped_column(String(40), nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False)
    modifiedAt: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    siteConfig: Mapped[List["SiteConfig"]] = relationship("SiteConfig", back_populates="address")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="address")

class Customer(Base):
    __tablename__ = "customers"

    customerId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    customerReference: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    #firstName: Mapped[str] = mapped_column(String(255), nullable=True)
    #lastName: Mapped[str] = mapped_column(String(255), nullable=False)
    #email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    #password: Mapped[str] = mapped_column(String(255), nullable=False)
    #phoneNumber: Mapped[str] = mapped_column(String(15), nullable=False)
    #companyNumber: Mapped[str] = mapped_column(String(255), nullable=True)
    signedUp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    #avatarPath: Mapped[str] = mapped_column(String(255), nullable=True)

    #businessSector: Mapped[Sector]
    #modifiedAt: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    addressId: Mapped[UUID] = mapped_column(ForeignKey("addresses.addressId"), nullable=False)
    address: Mapped["Address"] = relationship("Address", back_populates="customer")

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    cart: Mapped["Cart"] = relationship("Cart", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    orderId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    orderDate: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    #deliveryDate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    customerReference: Mapped[int] = mapped_column(ForeignKey("customers.customerReference"), nullable=False)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    #orderState: Mapped[OrderState]
    #selfCollect: Mapped[bool] = mapped_column(Boolean, default=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary=ordersProducts, back_populates="orders")
    routes: Mapped[List["Route"]] = relationship("Route", secondary=routesOrders, back_populates="orders")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="order")
    
class Product(Base):
    __tablename__ = "products"

    productId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    #description: Mapped[str] = mapped_column(String(255), nullable=False)
    #price: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    #imagePath: Mapped[str] = mapped_column(String(255), nullable=True)
    #modifiedAt: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    #createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())

    orders: Mapped[List["Order"]] = relationship("Order", secondary=ordersProducts, back_populates="products")
    categories: Mapped[List["Category"]] = relationship("Category", secondary=categoriesProducts, back_populates="products")

class Route(Base):
    __tablename__ = "routes"

    routeId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    orders: Mapped[List["Order"]] = relationship("Order", secondary=routesOrders, back_populates="routes")

class Category(Base):
    __tablename__ = "categories"

    categoryId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    imagePath: Mapped[str] = mapped_column(String(255), nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    products: Mapped[List["Product"]] = relationship("Product", secondary=categoriesProducts, back_populates="categories")

class Cart(Base):
    __tablename__ = "carts"

    cartId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    customerReference: Mapped[int] = mapped_column(ForeignKey("customers.customerReference"), nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="cart")

class Invoice(Base):
    __tablename__ = "invoices"

    invoiceId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    orderId: Mapped[UUID] = mapped_column(ForeignKey("orders.orderId"), nullable=False, unique=True)
    invoiceAmount: Mapped[int] = mapped_column(Integer, nullable=False)
    paymentDate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    #pdfUrl: Mapped[str] = mapped_column(String(255))

    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped["Order"] = relationship("Order", back_populates="invoice")

class Role(Base):
    __tablename__ = "roles"

    roleId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    #description: Mapped[str] = mapped_column(String(255), nullable=True)
    #deleted: Mapped[bool] = mapped_column(Boolean, default=False)

#Base.metadata.create_all(engine)