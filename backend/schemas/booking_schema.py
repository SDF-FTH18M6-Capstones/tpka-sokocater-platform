
from marshmallow import Schema, fields, validate


class BookingSchema(Schema):

    # Automatically generated primary key
    id = fields.Integer(dump_only=True)

    # Foreign key referencing the customer
    user_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Foreign key referencing the caterer
    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Foreign key referencing the selected package
    package_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Type of event
    event_type = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    # Date of the event
    event_date = fields.Date(required=True)

    # Location where the event will take place
    event_location = fields.String(
        required=True,
        validate=validate.Length(min=2, max=200)
    )

    # Number of guests attending
    guest_count = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Price charged per person
    price_per_person = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

    # Total estimated booking cost
    estimated_total = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

    # Booking status
    status = fields.String(
        dump_only=True
    )

    # Automatically generated creation timestamp
    created_at = fields.DateTime(dump_only=True)
