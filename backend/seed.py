
from datetime import date, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db

from models import (
    User,
    Caterer,
    Cuisine,
    CatererCuisine,
    Menu,
    MenuItem,
    Package,
    PackageItem,
    AddOn,
    Booking,
    BookingItem,
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_or_create(model, lookup, defaults=None):
    """
    Return an existing record or create a new one.

    Existing records are not overwritten.
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
# 1. SEED USERS
# ============================================================

def seed_users():

    print("Seeding users...")

    password_hash = generate_password_hash("SokoCater123!")

    admin = get_or_create(
        User,
        {"email": "admin@sokocater.com"},
        {
            "full_name": "SokoCater Admin",
            "password_hash": password_hash,
            "role": "admin",
            "phone_number": "0711000001",
        },
    )

    customer_one = get_or_create(
        User,
        {"email": "customer1@example.com"},
        {
            "full_name": "Jane Wanjiku",
            "password_hash": password_hash,
            "role": "customer",
            "phone_number": "0711000002",
        },
    )

    customer_two = get_or_create(
        User,
        {"email": "customer2@example.com"},
        {
            "full_name": "Brian Otieno",
            "password_hash": password_hash,
            "role": "customer",
            "phone_number": "0711000003",
        },
    )

    caterer_user_one = get_or_create(
        User,
        {"email": "greenplate@example.com"},
        {
            "full_name": "Mary Njeri",
            "password_hash": password_hash,
            "role": "caterer",
            "phone_number": "0711000004",
        },
    )

    caterer_user_two = get_or_create(
        User,
        {"email": "tastehub@example.com"},
        {
            "full_name": "David Mwangi",
            "password_hash": password_hash,
            "role": "caterer",
            "phone_number": "0711000005",
        },
    )

    return {
        "admin": admin,
        "customer_one": customer_one,
        "customer_two": customer_two,
        "caterer_user_one": caterer_user_one,
        "caterer_user_two": caterer_user_two,
    }


# ============================================================
# 2. SEED CATERERS
# ============================================================

def seed_caterers(users):

    print("Seeding caterers...")

    caterer_one = get_or_create(
        Caterer,
        {"user_id": users["caterer_user_one"].id},
        {
            "business_name": "Green Plate Catering",
            "description": "Fresh and delicious catering for weddings and events.",
            "location": "Nairobi",
            "contact_number": "0711222333",
            "verification_status": "pending",
        },
    )

    caterer_two = get_or_create(
        Caterer,
        {"user_id": users["caterer_user_two"].id},
        {
            "business_name": "Taste Hub Events",
            "description": "Professional catering for corporate and private events.",
            "location": "Kiambu",
            "contact_number": "0722333444",
            "verification_status": "pending",
        },
    )

    return {
        "caterer_one": caterer_one,
        "caterer_two": caterer_two,
    }


# ============================================================
# 3. SEED CUISINES
# ============================================================

def seed_cuisines():

    print("Seeding cuisines...")

    kenyan = get_or_create(
        Cuisine,
        {"cuisine_name": "Kenyan"},
    )

    continental = get_or_create(
        Cuisine,
        {"cuisine_name": "Continental"},
    )

    indian = get_or_create(
        Cuisine,
        {"cuisine_name": "Indian"},
    )

    return {
        "kenyan": kenyan,
        "continental": continental,
        "indian": indian,
    }


# ============================================================
# 4. ASSIGN CUISINES TO CATERERS
# ============================================================

def seed_caterer_cuisines(caterers, cuisines):

    print("Assigning cuisines to caterers...")

    assignments = [
        (caterers["caterer_one"], cuisines["kenyan"]),
        (caterers["caterer_one"], cuisines["continental"]),
        (caterers["caterer_two"], cuisines["kenyan"]),
        (caterers["caterer_two"], cuisines["indian"]),
    ]

    for caterer, cuisine in assignments:

        get_or_create(
            CatererCuisine,
            {
                "caterer_id": caterer.id,
                "cuisine_id": cuisine.id,
            },
        )


# ============================================================
# 5. SEED MENUS
# ============================================================

def seed_menus(caterers):

    print("Seeding menus...")

    menu_one = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_one"].id,
            "menu_name": "Wedding Menu",
        },
        {
            "description": "A selection of meals suitable for weddings.",
        },
    )

    menu_two = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_two"].id,
            "menu_name": "Corporate Menu",
        },
        {
            "description": "Professional catering options for corporate events.",
        },
    )

    return {
        "menu_one": menu_one,
        "menu_two": menu_two,
    }


# ============================================================
# 6. SEED MENU ITEMS
# ============================================================

def seed_menu_items(menus):

    print("Seeding menu items...")

    chicken_pilau = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_one"].id,
            "item_name": "Chicken Pilau",
        },
        {
            "description": "Kenyan spiced rice served with chicken.",
            "price": Decimal("500.00"),
        },
    )

    chapati = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_one"].id,
            "item_name": "Chapati",
        },
        {
            "description": "Freshly prepared Kenyan chapati.",
            "price": Decimal("100.00"),
        },
    )

    vegetable_rice = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_two"].id,
            "item_name": "Vegetable Rice",
        },
        {
            "description": "Rice prepared with assorted vegetables.",
            "price": Decimal("350.00"),
        },
    )

    grilled_chicken = get_or_create(
        MenuItem,
        {
            "menu_id": menus["menu_two"].id,
            "item_name": "Grilled Chicken",
        },
        {
            "description": "Seasoned grilled chicken.",
            "price": Decimal("600.00"),
        },
    )

    return {
        "chicken_pilau": chicken_pilau,
        "chapati": chapati,
        "vegetable_rice": vegetable_rice,
        "grilled_chicken": grilled_chicken,
    }


# ============================================================
# 7. SEED PACKAGES
# ============================================================

def seed_packages(caterers):

    print("Seeding packages...")

    package_one = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_one"].id,
            "package_name": "Classic Wedding Package",
        },
        {
            "description": "A complete wedding catering package.",
            "price_per_guest": Decimal("1500.00"),
            "minimum_guests": 20,
            "maximum_guests": 300,
        },
    )

    package_two = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_two"].id,
            "package_name": "Corporate Lunch Package",
        },
        {
            "description": "A convenient package for corporate events.",
            "price_per_guest": Decimal("1200.00"),
            "minimum_guests": 10,
            "maximum_guests": 200,
        },
    )

    return {
        "package_one": package_one,
        "package_two": package_two,
    }


# ============================================================
# 8. CONNECT PACKAGES TO MENU ITEMS
# ============================================================

def seed_package_items(packages, menu_items):

    print("Connecting packages to menu items...")

    assignments = [
        (packages["package_one"], menu_items["chicken_pilau"]),
        (packages["package_one"], menu_items["chapati"]),
        (packages["package_two"], menu_items["vegetable_rice"]),
        (packages["package_two"], menu_items["grilled_chicken"]),
    ]

    for package, menu_item in assignments:

        get_or_create(
            PackageItem,
            {
                "package_id": package.id,
                "menu_item_id": menu_item.id,
            },
        )


# ============================================================
# 9. SEED ADD-ONS
# ============================================================

def seed_add_ons(caterers):

    print("Seeding add-ons...")

    juice_service = get_or_create(
        AddOn,
        {
            "caterer_id": caterers["caterer_one"].id,
            "addon_name": "Fresh Juice Service",
        },
        {
            "description": "Freshly prepared juice service.",
            "price": Decimal("5000.00"),
        },
    )

    waiter_service = get_or_create(
        AddOn,
        {
            "caterer_id": caterers["caterer_two"].id,
            "addon_name": "Waiter Service",
        },
        {
            "description": "Professional waiter service for events.",
            "price": Decimal("8000.00"),
        },
    )

    return {
        "juice_service": juice_service,
        "waiter_service": waiter_service,
    }


# ============================================================
# 10. SEED BOOKINGS
# ============================================================

def seed_bookings(users, caterers):

    print("Seeding bookings...")

    booking_one = get_or_create(
        Booking,
        {
            "customer_id": users["customer_one"].id,
            "caterer_id": caterers["caterer_one"].id,
            "event_type": "Wedding",
        },
        {
            "event_date": date.today() + timedelta(days=30),
            "event_location": "Nairobi",
            "guest_count": 80,
            "estimated_total": Decimal("120000.00"),
            "status": "pending",
        },
    )

    booking_two = get_or_create(
        Booking,
        {
            "customer_id": users["customer_two"].id,
            "caterer_id": caterers["caterer_two"].id,
            "event_type": "Corporate Event",
        },
        {
            "event_date": date.today() + timedelta(days=60),
            "event_location": "Kiambu",
            "guest_count": 50,
            "estimated_total": Decimal("60000.00"),
            "status": "confirmed",
        },
    )

    return {
        "booking_one": booking_one,
        "booking_two": booking_two,
    }


# ============================================================
# 11. CONNECT BOOKINGS TO PACKAGES AND ADD-ONS
# ============================================================

def seed_booking_items(bookings, packages, add_ons):

    print("Connecting bookings to packages and add-ons...")

    # First booking: wedding package.
    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_one"].id,
            "package_id": packages["package_one"].id,
        },
        {
            "addon_id": None,
            "quantity": 80,
            "unit_price": Decimal("1500.00"),
        },
    )

    # Second booking: corporate package.
    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_two"].id,
            "package_id": packages["package_two"].id,
        },
        {
            "addon_id": None,
            "quantity": 50,
            "unit_price": Decimal("1200.00"),
        },
    )

    # Second booking: waiter service add-on.
    get_or_create(
        BookingItem,
        {
            "booking_id": bookings["booking_two"].id,
            "addon_id": add_ons["waiter_service"].id,
        },
        {
            "package_id": None,
            "quantity": 1,
            "unit_price": Decimal("8000.00"),
        },
    )


# ============================================================
# 12. MAIN SEED FUNCTION
# ============================================================

def seed_database():

    print("\nStarting SokoCater database seeding...\n")

    try:

        users = seed_users()

        caterers = seed_caterers(users)

        cuisines = seed_cuisines()

        seed_caterer_cuisines(caterers, cuisines)

        menus = seed_menus(caterers)

        menu_items = seed_menu_items(menus)

        packages = seed_packages(caterers)

        seed_package_items(packages, menu_items)

        add_ons = seed_add_ons(caterers)

        bookings = seed_bookings(users, caterers)

        seed_booking_items(bookings, packages, add_ons)

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
