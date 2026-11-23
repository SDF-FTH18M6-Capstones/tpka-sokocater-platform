from marshmallow import Schema, fields, validate, EXCLUDE

class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
    phone_number = fields.String(
        required=False,
        allow_none=True
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(["customer", "caterer"])
    )

class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
