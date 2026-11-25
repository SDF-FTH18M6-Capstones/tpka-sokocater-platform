from marshmallow import Schema, fields, validate, validates


class MenuItemSchema(Schema):

    id = fields.Integer(dump_only=True)

    menu_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    item_name = fields.String(
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

    image_url = fields.String(
        allow_none=True,
        validate=validate.Length(max=255)
    )

    @validates("item_name")
    def validate_item_name(self, value, **kwargs):

        if not value.strip():
            from marshmallow import ValidationError

            raise ValidationError(
                "Menu item name cannot contain only spaces."
            )