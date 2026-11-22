
from marshmallow import Schema, fields, validate, validates, ValidationError


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

    description = fields.String(allow_none=True)

    location = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    contact_number = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(min=7, max=20)
    )

    business_image = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255)
    )

    verification_status = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("business_name")
    def validate_business_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError(
                "Business name cannot contain only spaces."
            )

    @validates("location")
    def validate_location(self, value, **kwargs):
        if not value.strip():
            raise ValidationError(
                "Location cannot contain only spaces."
            )
