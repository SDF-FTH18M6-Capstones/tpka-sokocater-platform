
from marshmallow import Schema, fields, validate


class PackageSchema(Schema):

    # Automatically generated primary key
    id = fields.Integer(dump_only=True)

    # Foreign key referencing the caterer who owns the package
    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Package name
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    # Package category: only the four approved options
    category = fields.String(
        required=True,
        validate=validate.OneOf([
            "Food Catering",
            "Wedding Catering",
            "Corporate Events",
            "Private Parties"
        ])
    )

    # Optional package description
    description = fields.String(allow_none=True)

    # Automatically generated timestamp
    created_at = fields.DateTime(dump_only=True)
