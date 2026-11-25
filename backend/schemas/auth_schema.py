from marshmallow import Schema, fields, validate, pre_load, EXCLUDE


class BaseAuthSchema(Schema):

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalize_email(self, data, **kwargs):
        """
        Remove surrounding spaces and lowercase email
        before validation.
        """
        if isinstance(data, dict):
            data = data.copy()

            if isinstance(data.get("email"), str):
                data["email"] = data["email"].strip().lower()

        return data


# ============================================================
# REGISTER SCHEMA
# ============================================================

class RegisterSchema(BaseAuthSchema):

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


# ============================================================
# LOGIN SCHEMA
# ============================================================

class LoginSchema(BaseAuthSchema):

    email = fields.Email(required=True)

    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=1)
    )
