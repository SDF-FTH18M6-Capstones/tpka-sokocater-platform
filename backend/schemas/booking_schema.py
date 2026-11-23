
from datetime import date

from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    validates_schema,
    ValidationError
)


class BookingSchema(Schema):

    id = fields.Integer(dump_only=True)

    customer_id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Used as input to select a package.
    # The package selection will be stored in booking_items.
    package_id = fields.Integer(
        required=True,
        load_only=True,
        validate=validate.Range(min=1)
    )

    event_type = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    event_date = fields.Date(required=True)

    event_start_time = fields.Time(required=True)

    event_end_time = fields.Time(required=True)

    event_location = fields.String(
        required=True,
        validate=validate.Length(min=2, max=200)
    )

    guest_count = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    estimated_total = fields.Decimal(
        dump_only=True,
        as_string=True
    )

    status = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("event_date")
    def validate_event_date(self, value, **kwargs):
        if value < date.today():
            raise ValidationError(
                "Event date cannot be in the past."
            )

    @validates_schema
    def validate_event_time_range(self, data, **kwargs):
        start_time = data.get("event_start_time")
        end_time = data.get("event_end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time >= end_time
        ):
            raise ValidationError({
                "event_end_time": [
                    "Event end time must be later than event start time."
                ]
            })
