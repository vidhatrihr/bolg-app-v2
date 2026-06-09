from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    slug = Column(String)
    description = Column(Text)
    brand = Column(String)
    category = Column(String)
    price = Column(Float)


class Visitor(db.Model):
    __tablename__ = "visitors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_uuid = Column(String, unique=True)
    user_agent = Column(String)
    ip_address = Column(String)
    first_seen = Column(DateTime, default=datetime)

    visits = relationship("Visit", backref="visitor")


class Visit(db.Model):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    url = Column(String)
    page_type = Column(String)
    entity_info = Column(String)
    time_stamp = Column(DateTime, default=datetime)


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_uuid = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product = relationship("Product")
