from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    ValidationError
)


ALLOWED_ADDON_TYPES = [
    "venue",
    "chairs",
    "tables",
    "materials"
]


class AddOnSchema(Schema):

    id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    addon_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    description = fields.String(
        allow_none=True
    )

    price = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

    addon_type = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(
            ALLOWED_ADDON_TYPES,
            error="Add-on type must be venue, chairs, tables, or materials."
        )
    )

    @validates("addon_name")
    def validate_addon_name(self, value, **kwargs):

        if not value.strip():
            raise ValidationError(
                "Add-on name cannot contain only spaces."
            )