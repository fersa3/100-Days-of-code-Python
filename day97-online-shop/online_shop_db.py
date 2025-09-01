import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, scoped_session
from sqlalchemy import Integer, String, Float, Text, ForeignKey, UniqueConstraint, func, create_engine
from flask_login import UserMixin
import os


# CREATE DATABASE
db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True

# CONFIGUE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    image: Mapped[str] = mapped_column(String(200), unique=True)
    size: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)
    colors: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stars: Mapped[int] = mapped_column(Integer)
    qty_in_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    # Relationship to ProductSize table:
    sizes = db.relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")

class ProductSize(db.Model):
    __tablename__ = "product_sizes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    size: Mapped[str] = mapped_column(String(10), nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Relationship to Product table:
    product = db.relationship("Product", back_populates="sizes")

    # Composite unique constraint to ensure a product doesn't have duplicate sizes:
    __table_args__ = (UniqueConstraint('product_id', 'size', name='_product_size_uc'),)


# DATABASE SETUP
def init_db(app=None, csv_file="data/products.csv"):
    db_uri = os.environ.get('DB_URI_challenges', "sqlite:///instance/online_shop.db")
    engine = create_engine(db_uri)
    db.metadata.create_all(engine)

    if app:
        # Set up session with app context.
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        db.session = Session

        # Check if users table is empty and create a default user if it is
        if db.session.query(User).first() is None:
            from werkzeug.security import generate_password_hash
            default_user = User(
                email="fer@shtmail.com",
                username="fersa",
                password=generate_password_hash("aaaaa5", method='pbkdf2:sha256'),
                name="Admin User"
            )
            db.session.add(default_user)
            db.session.commit()

    # If products table is empty, populate it from csv in data folder:
    if db.session.query(Product).first() is None and os.path.exists(csv_file):
        products_df = pd.read_csv(csv_file)
        populate_products_db(db.session, products_df)
    # If product_sizes table is empty, populate it based on existing products
    if db.session.query(ProductSize).first() is None and db.session.query(Product).first() is not None:
        populate_product_sizes_randomly(db.session)
    return engine

def populate_products_db(session, products_df):
    """ Loads initial dummy data from csv file to have products to display. """
    # print(f"Data frame columns: {products_df.columns}")
    products = [
        Product(
            id=row["id"],
            name=row["name"],
            image=row["image"],
            size=row["size"],
            description=row["description"],
            colors=row["colors"],
            price=row["price"],
            stars=row["stars"],
            qty_in_stock=row["qty_in_stock"]
        )
        for _, row in products_df.iterrows()
    ]
    session.add_all(products)
    session.commit()


def populate_product_sizes_randomly(session):
    """ Populates product_sizes table with random inventory values and updates the main product inventory. """
    import random

    products = session.query(Product).all()

    for product in products:
        sizes = product.size.split()  # Parse sizes from the size field.
        total_inventory = 0  # Variable to track total inventory.

        # Create ProductSize records with random inventory.
        for size in sizes:
            random_qty = random.randint(5, 50)  # Get a random int between 5 and 50.
            total_inventory += random_qty

            product_size = ProductSize(
                product_id=product.id,
                size=size,
                qty_in_stock=random_qty
            )
            session.add(product_size)

        # Update the main product's inventory to match the sum:
        product.qty_in_stock = total_inventory

    session.commit()


def update_product_inventory(session, product_id):
    """ Function that updates the main product qty_in_stock based on the sum of all it's sizes inventory. """
    total_qty = session.query(func.sum(ProductSize.qty_in_stock))\
                    .filter(ProductSize.product_id == product_id)\
                    .scalar() or 0
    product = session.query(Product).get(product_id)
    if product:
        product.qty_in_stock = total_qty
        session.commit()