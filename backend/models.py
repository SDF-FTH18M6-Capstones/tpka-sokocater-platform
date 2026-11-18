
from datetime import datetime

from sqlalchemy import CheckConstraint, UniqueConstraint

from extensions import db


# ============================================================
# 1. USER MODEL
# ============================================================

class User(db.Model):
    __tablename__ = "users"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'caterer', 'admin')",
            name="check_user_role"
        ),
    )

    # Relationships
    caterer = db.relationship(
        "Caterer",
        back_populates="user",
        uselist=False
    )

    bookings = db.relationship(
        "Booking",
        back_populates="user"
    )

    orders = db.relationship(
        "Order",
        back_populates="user"
    )


# ============================================================
# 2. CATERER MODEL
# ============================================================

class Caterer(db.Model):
    __tablename__ = "caterers"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing users.id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    business_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    contact_number = db.Column(db.String(20))

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="caterer"
    )

    menus = db.relationship(
        "Menu",
        back_populates="caterer"
    )

    packages = db.relationship(
        "Package",
        back_populates="caterer"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="caterer"
    )

    orders = db.relationship(
        "Order",
        back_populates="caterer"
    )


# ============================================================
# 3. MENU MODEL
# ============================================================

class Menu(db.Model):
    __tablename__ = "menus"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing caterers.id
    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterers.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="check_menu_price"
        ),
    )

    # Relationships
    caterer = db.relationship(
        "Caterer",
        back_populates="menus"
    )

    orders = db.relationship(
        "Order",
        back_populates="menu"
    )


# ============================================================
# 4. PACKAGE MODEL
# ============================================================

class Package(db.Model):
    __tablename__ = "packages"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing caterers.id
    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterers.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('Food Catering', 'Wedding Catering', "
            "'Corporate Events', 'Private Parties')",
            name="check_package_category"
        ),
    )

    # Relationships
    caterer = db.relationship(
        "Caterer",
        back_populates="packages"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="package"
    )


# ============================================================
# 5. BOOKING MODEL
# ============================================================

class Booking(db.Model):
    __tablename__ = "bookings"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing users.id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Foreign key referencing caterers.id
    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterers.id"),
        nullable=False
    )

    # Foreign key referencing packages.id
    package_id = db.Column(
        db.Integer,
        db.ForeignKey("packages.id"),
        nullable=False
    )

    event_type = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_location = db.Column(db.String(200), nullable=False)

    guest_count = db.Column(db.Integer, nullable=False)

    price_per_person = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    estimated_total = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "guest_count > 0",
            name="check_booking_guest_count"
        ),
        CheckConstraint(
            "price_per_person >= 0",
            name="check_booking_price_per_person"
        ),
        CheckConstraint(
            "estimated_total >= 0",
            name="check_booking_total"
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', "
            "'confirmed', 'cancelled', 'completed')",
            name="check_booking_status"
        ),
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="bookings"
    )

    caterer = db.relationship(
        "Caterer",
        back_populates="bookings"
    )

    package = db.relationship(
        "Package",
        back_populates="bookings"
    )


# ============================================================
# 6. ORDER MODEL
# ============================================================

class Order(db.Model):
    __tablename__ = "orders"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing users.id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Foreign key referencing caterers.id
    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterers.id"),
        nullable=False
    )

    # Foreign key referencing menus.id
    menu_id = db.Column(
        db.Integer,
        db.ForeignKey("menus.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    order_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_order_quantity"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="check_order_unit_price"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_total"
        ),
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="orders"
    )

    caterer = db.relationship(
        "Caterer",
        back_populates="orders"
    )

    menu = db.relationship(
        "Menu",
        back_populates="orders"
    )
