
from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError
)


class PackageSchema(Schema):

    # Automatically generated package ID
    id = fields.Integer(dump_only=True)

    # Caterer who owns the package
    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Package name
    package_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    # Optional description
    description = fields.String(allow_none=True)

    # Price charged per guest
    price_per_guest = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0.01)
    )

    # Minimum number of guests
    minimum_guests = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Maximum number of guests
    maximum_guests = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1)
    )

    # Ensure maximum guests is not less than minimum guests
    @validates_schema
    def validate_guest_range(self, data, **kwargs):

        minimum = data.get("minimum_guests")
        maximum = data.get("maximum_guests")

        if (
            minimum is not None
            and maximum is not None
            and maximum < minimum
        ):
            raise ValidationError(
                "Maximum guests cannot be less than minimum guests.",
                field_name="maximum_guests"
            )
