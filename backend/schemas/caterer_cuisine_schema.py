from marshmallow import Schema, fields, validate


class CatererCuisineSchema(Schema):

    class Meta:
        unknown = "raise"

    id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    cuisine_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )