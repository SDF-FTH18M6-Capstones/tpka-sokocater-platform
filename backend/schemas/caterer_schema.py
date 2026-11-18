
from marshmallow import Schema, fields, validate


class CatererSchema(Schema):

    id = fields.Integer(dump_only=True)

    user_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    business_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    location = fields.String(
        required=True,
        validate=validate.Length(min=2, max=255)
    )

    description = fields.String(allow_none=True)

    contact_number = fields.String(
        required=True,
        validate=validate.Length(min=7, max=20)
    )

    created_at = fields.DateTime(dump_only=True)
