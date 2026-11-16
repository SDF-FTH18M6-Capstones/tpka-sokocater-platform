
from marshmallow import Schema, fields, validate


class MenuSchema(Schema):

    # Automatically generated menu ID
    id = fields.Integer(dump_only=True)

    # The caterer who owns this menu
    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Name of the menu
    menu_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    # Optional menu description
    description = fields.String(allow_none=True)

    # Automatically generated creation date
    created_at = fields.DateTime(dump_only=True)

