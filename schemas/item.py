from marshmallow import Schema, fields

class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    user_id = fields.Int(dump_only=True)

class ItemUpdateSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)
