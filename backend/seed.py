
from datetime import date, datetime, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db

from models import (
    User,
    CatererProfile,
    Menu,
    MenuItem,
    Package,
    PackageItem,
    AddOn,
    Booking,
    BookingItem,
    Availability,
    Payment,
    Review,
    Notification
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_or_create(model, lookup, defaults=None):
    """
    Find an existing record or create a new one.

    Prevents duplicate seed records when the script
    is executed multiple times.
    """

    record = db.session.query(model).filter_by(**lookup).first()

    if record:
        return record

    values = dict(lookup)

    if defaults:
        values.update(defaults)

    record = model(**values)

    db.session.add(record)
    db.session.flush()

    return record


# ============================================================
# SEED USERS
# ============================================================

def seed_users():

    print("Seeding users...")

    sample_password = generate_password_hash("SokoCater123!")

    admin = get_or_create(
        User,
        {"email": "admin@sokocater.com"},
        {
            "full_name": "SokoCater Admin",
            "password_hash": sample_password,
            "role": "admin",
            "phone_number": "0711000001"
        }
    )

    customer_one = get_or_create(
        User,
        {"email": "customer1@example.com"},
        {
            "full_name": "Jane Wanjiku",
            "password_hash": sample_password,
            "role": "customer",
            "phone_number": "0711000002"
        }
    )

    customer_two = get_or_create(
        User,
        {"email": "customer2@example.com"},
        {
            "full_name": "Brian Otieno",
            "password_hash": sample_password,
            "role": "customer",
            "phone_number": "0711000003"
        }
    )

    caterer_user_one = get_or_create(
        User,
        {"email": "greenplate@example.com"},
        {
            "full_name": "Mary Njeri",
            "password_hash": sample_password,
            "role": "caterer",
            "phone_number": "0711000004"
        }
    )

    caterer_user_two = get_or_create(
        User,
        {"email": "tastehub@example.com"},
        {
            "full_name": "David Mwangi",
            "password_hash": sample_password,
            "role": "caterer",
            "phone_number": "0711000005"
        }
    )

    return {
        "admin": admin,
        "customer_one": customer_one,
        "customer_two": customer_two,
        "caterer_user_one": caterer_user_one,
        "caterer_user_two": caterer_user_two
    }


# ============================================================
# SEED CATERER PROFILES
# ============================================================

def seed_caterers(users):

    print("Seeding caterer profiles...")

    caterer_one = get_or_create(
        CatererProfile,
        {"user_id": users["caterer_user_one"].id},
        {
            "business_name": "Green Plate Catering",
            "description": "Fresh and delicious catering for weddings and events.",
            "location": "Nairobi",
            "contact_number": "0711222333",
            "business_image": None,
            "verification_status": "verified"
        }
    )

    caterer_two = get_or_create(
        CatererProfile,
        {"user_id": users["caterer_user_two"].id},
        {
            "business_name": "Taste Hub Events",
            "description": "Professional catering for corporate and private events.",
            "location": "Kiambu",
            "contact_number": "0722333444",
            "business_image": None,
            "verification_status": "verified"
        }
    )

    return {
        "caterer_one": caterer_one,
        "caterer_two": caterer_two
    }


# ============================================================
# SEED MENUS
# ============================================================

def seed_menus(caterers):

    print("Seeding menus...")

    menu_one = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_one"].id,
            "menu_name": "Wedding Menu"
        },
        {
            "description": "A selection of meals suitable for weddings."
        }
    )

    menu_two = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_two"].id,
            "menu_name": "Corporate Menu"
        },
        {
            "description": "Professional catering options for corporate events."
        }
    )

    return {
        "menu_one": menu_one,
        "menu_two": menu_two
    }


# ============================================================
# SEED MENU ITEMS
# ============================================================

def seed_menu_items(menus):

    print("Seeding menu items...")

    pilau = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_one"].id,
            "item_name": "Chicken Pilau"
        },
        {
            "description": "Kenyan spiced rice served with chicken.",
            "price": Decimal("350.00"),
            "image_url": None
        }
    )

    chapati = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_one"].id,
            "item_name": "Chapati"
        },
        {
            "description": "Freshly prepared Kenyan chapati.",
            "price": Decimal("50.00"),
            "image_url": None
        }
    )

    vegetables = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_two"].id,
            "item_name": "Vegetable Rice"
        },
        {
            "description": "Seasoned rice served with fresh vegetables.",
            "price": Decimal("250.00"),
            "image_url": None
        }
    )

    chicken = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_two"].id,
            "item_name": "Grilled Chicken"
        },
        {
            "description": "Grilled chicken with herbs and spices.",
            "price": Decimal("400.00"),
            "image_url": None
        }
    )

    return {
        "pilau": pilau,
        "chapati": chapati,
        "vegetables": vegetables,
        "chicken": chicken
    }


# ============================================================
# SEED PACKAGES
# ============================================================

def seed_packages(caterers):

    print("Seeding packages...")

    package_one = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_one"].id,
            "package_name": "Classic Wedding Package"
        },
        {
            "description": "A complete wedding catering package.",
            "price_per_guest": Decimal("1500.00"),
            "minimum_guests": 20,
            "maximum_guests": 200
        }
    )

    package_two = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_two"].id,
            "package_name": "Corporate Lunch Package"
        },
        {
            "description": "A convenient package for corporate events.",
            "price_per_guest": Decimal("1200.00"),
            "minimum_guests": 10,
            "maximum_guests": 150
        }
    )

    return {
        "package_one": package_one,
        "package_two": package_two
    }


# ============================================================
# SEED PACKAGE ITEMS
# ============================================================

def seed_package_items(packages, menu_items):

    print("Seeding package items...")

    get_or_create(
        PackageItem,
        {
            "package_id": packages["package_one"].id,
            "menu_item_id": menu_items["pilau"].id
        }
    )

    get_or_create(
        PackageItem,
        {
            "package_id": packages["package_one"].id,
            "menu_item_id": menu_items["chapati"].id
        }
    )

    get_or_create(
        PackageItem,
        {
            "package_id": packages["package_two"].id,
            "menu_item_id": menu_items["vegetables"].id
        }
    )

    get_or_create(
        PackageItem,
        {
            "package_id": packages["package_two"].id,
            "menu_item_id": menu_items["chicken"].id
        }
    )


# ============================================================
# SEED ADD-ONS
# ============================================================

def seed_addons(caterers):

    print("Seeding add-ons...")

    addon_one = get_or_create(
        AddOn,
        {
            "caterer_id": caterers["caterer_one"].id,
            "addon_name": "Fresh Juice Service"
        },
        {
            "description": "Fresh juice served to event guests.",
            "price": Decimal("5000.00")
        }
    )

    addon_two = get_or_create(
        AddOn,
        {
            "caterer_id": caterers["caterer_two"].id,
            "addon_name": "Waiter Service"
        },
        {
            "description": "Professional waiter service for events.",
            "price": Decimal("8000.00")
        }
    )

    return {
        "addon_one": addon_one,
        "addon_two": addon_two
    }


# ============================================================
# SEED BOOKINGS
# ============================================================

def seed_bookings(users, caterers):

    print("Seeding bookings...")

    booking_one = get_or_create(
        Booking,
        {
            "customer_id": users["customer_one"].id,
            "caterer_id": caterers["caterer_one"].id,
            "event_date": date.today() + timedelta(days=30),
            "event_type": "Wedding"
        },
        {
            "event_location": "Nairobi",
            "guest_count": 80,
            "estimated_total": Decimal("120000.00"),
            "status": "pending"
        }
    )

    booking_two = get_or_create(
        Booking,
        {
            "customer_id": users["customer_two"].id,
            "caterer_id": caterers["caterer_two"].id,
            "event_date": date.today() - timedelta(days=30),
            "event_type": "Corporate Event"
        },
        {
            "event_location": "Kiambu",
            "guest_count": 50,
            "estimated_total": Decimal("68000.00"),
            "status": "completed"
        }
    )

    return {
        "booking_one": booking_one,
        "booking_two": booking_two
    }


# ============================================================
# SEED BOOKING ITEMS
# ============================================================

def seed_booking_items(bookings, packages, addons):

    print("Seeding booking items...")

    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_one"].id,
            "package_id": packages["package_one"].id,
            "addon_id": None
        },
        {
            "quantity": 80,
            "unit_price": Decimal("1500.00")
        }
    )

    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_two"].id,
            "package_id": packages["package_two"].id,
            "addon_id": None
        },
        {
            "quantity": 50,
            "unit_price": Decimal("1200.00")
        }
    )

    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_two"].id,
            "package_id": None,
            "addon_id": addons["addon_two"].id
        },
        {
            "quantity": 1,
            "unit_price": Decimal("8000.00")
        }
    )


# ============================================================
# SEED AVAILABILITY
# ============================================================

def seed_availability(caterers):

    print("Seeding availability...")

    get_or_create(
        Availability,
        {
            "caterer_id": caterers["caterer_one"].id,
            "available_date": date.today() + timedelta(days=30)
        },
        {
            "status": "booked"
        }
    )

    get_or_create(
        Availability,
        {
            "caterer_id": caterers["caterer_one"].id,
            "available_date": date.today() + timedelta(days=31)
        },
        {
            "status": "available"
        }
    )

    get_or_create(
        Availability,
        {
            "caterer_id": caterers["caterer_two"].id,
            "available_date": date.today() + timedelta(days=30)
        },
        {
            "status": "available"
        }
    )


# ============================================================
# SEED PAYMENTS
# ============================================================

def seed_payments(bookings):

    print("Seeding payments...")

    get_or_create(
        Payment,
        {
            "transaction_reference": "SEED-PAYMENT-001"
        },
        {
            "booking_id": bookings["booking_one"].id,
            "amount": Decimal("120000.00"),
            "payment_method": "M-Pesa",
            "payment_status": "pending",
            "paid_at": None
        }
    )

    get_or_create(
        Payment,
        {
            "transaction_reference": "SEED-PAYMENT-002"
        },
        {
            "booking_id": bookings["booking_two"].id,
            "amount": Decimal("68000.00"),
            "payment_method": "M-Pesa",
            "payment_status": "successful",
            "paid_at": datetime.utcnow()
        }
    )


# ============================================================
# SEED REVIEWS
# ============================================================

def seed_reviews(users, caterers, bookings):

    print("Seeding reviews...")

    get_or_create(
        Review,
        {
            "booking_id": bookings["booking_two"].id
        },
        {
            "customer_id": users["customer_two"].id,
            "caterer_id": caterers["caterer_two"].id,
            "rating": 5,
            "comment": "Excellent catering service. The food was delicious!"
        }
    )


# ============================================================
# SEED NOTIFICATIONS
# ============================================================

def seed_notifications(users):

    print("Seeding notifications...")

    get_or_create(
        Notification,
        {
            "user_id": users["customer_one"].id,
            "message": "Your wedding booking request has been submitted.",
            "notification_type": "booking"
        },
        {
            "is_read": False
        }
    )

    get_or_create(
        Notification,
        {
            "user_id": users["caterer_user_one"].id,
            "message": "You have received a new booking request.",
            "notification_type": "booking"
        },
        {
            "is_read": False
        }
    )

    get_or_create(
        Notification,
        {
            "user_id": users["customer_two"].id,
            "message": "Your corporate event booking has been completed.",
            "notification_type": "booking"
        },
        {
            "is_read": True
        }
    )


# ============================================================
# MAIN SEED FUNCTION
# ============================================================

def seed_database():

    print("\nStarting SokoCater database seeding...\n")

    try:

        # Create missing tables without deleting existing data
        db.create_all()

        # Seed records in foreign-key dependency order
        users = seed_users()

        caterers = seed_caterers(users)

        menus = seed_menus(caterers)

        menu_items = seed_menu_items(menus)

        packages = seed_packages(caterers)

        seed_package_items(packages, menu_items)

        addons = seed_addons(caterers)

        bookings = seed_bookings(users, caterers)

        seed_booking_items(bookings, packages, addons)

        seed_availability(caterers)

        seed_payments(bookings)

        seed_reviews(users, caterers, bookings)

        seed_notifications(users)

        # Save all changes
        db.session.commit()

        print("\n========================================")
        print("SokoCater database seeded successfully!")
        print("========================================")

        print("\nSample login accounts:")
        print("Admin:     admin@sokocater.com")
        print("Customer:  customer1@example.com")
        print("Caterer:   greenplate@example.com")
        print("Password:  SokoCater123!")

        print("\n========================================\n")

    except Exception as error:

        # Undo changes if anything goes wrong
        db.session.rollback()

        print("\nDatabase seeding failed!")
        print(f"Error: {error}")

        raise


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app = create_app()

    with app.app_context():
        seed_database()
