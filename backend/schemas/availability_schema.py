from datetime import date
from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    validates_schema,
    ValidationError
)


class AvailabilitySchema(Schema):

    id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    available_date = fields.Date(
        required=True
    )

    start_time = fields.Time(
        required=True
    )

    end_time = fields.Time(
        required=True
    )

    status = fields.String(
        required=True,
        validate=validate.OneOf(["available", "unavailable"])
    )

    @validates("available_date")
    def validate_available_date(self, value, **kwargs):
        if value < date.today():
            raise ValidationError(
                "Availability date cannot be in the past."
            )

    @validates_schema
    def validate_time_range(self, data, **kwargs):

        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time >= end_time
        ):
            raise ValidationError({
                "end_time": [
                    "End time must be later than start time."
                ]
            })
