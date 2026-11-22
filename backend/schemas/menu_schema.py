from marshmallow import Schema, fields, validate, validates, ValidationError


class MenuSchema(Schema):

    id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    menu_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    description = fields.String(allow_none=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("menu_name")
    def validate_menu_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError(
                "Menu name cannot contain only spaces."
            )
