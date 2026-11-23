from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    ValidationError,
    pre_load
)


class CuisineSchema(Schema):

    class Meta:
        unknown = "raise"

    id = fields.Integer(dump_only=True)

    cuisine_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    @pre_load
    def normalize_cuisine_name(self, data, **kwargs):
        if isinstance(data, dict):
            name = data.get("cuisine_name")

            if isinstance(name, str):
                data["cuisine_name"] = name.strip()

        return data

    @validates("cuisine_name")
    def validate_cuisine_name(self, value, **kwargs):

        if not value:
            raise ValidationError(
                "Cuisine name cannot be empty."
            )