
from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError
)


class PackageSchema(Schema):

    id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    package_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    description = fields.String(
        allow_none=True
    )

    price_per_guest = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

    minimum_guests = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    maximum_guests = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1)
    )

    @validates_schema
    def validate_guest_range(self, data, **kwargs):

        minimum = data.get("minimum_guests")
        maximum = data.get("maximum_guests")

        if (
            minimum is not None
            and maximum is not None
            and maximum < minimum
        ):
            raise ValidationError({
                "maximum_guests": [
                    "Maximum guests must be greater than or equal to minimum guests."
                ]
            })
