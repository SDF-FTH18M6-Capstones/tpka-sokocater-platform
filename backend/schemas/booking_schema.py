
from marshmallow import Schema, fields, validate


class BookingSchema(Schema):
    # Automatically generated booking ID
    id = fields.Integer(dump_only=True)

    # Customer making the booking
    customer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Caterer receiving the booking
    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Date of the event
    event_date = fields.Date(required=True)

    # Type of event (wedding, birthday, corporate, etc.)
    event_type = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

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

    # Estimated total booking cost
    estimated_total = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

    # Booking status is managed by the system
    status = fields.String(dump_only=True)

    # Automatically generated booking creation date
    created_at = fields.DateTime(dump_only=True)
