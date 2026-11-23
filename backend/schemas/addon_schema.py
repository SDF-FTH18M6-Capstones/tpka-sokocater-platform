from marshmallow import (
    Schema,
    fields,
    validate,
    validates
)
from marshmallow import ValidationError


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

    @validates("addon_name")
    def validate_addon_name(self, value, **kwargs):

        if not value.strip():
            raise ValidationError(
                "Add-on name cannot contain only spaces."
            )