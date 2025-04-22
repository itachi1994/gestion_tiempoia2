from app import ma
from marshmallow import fields, validate

class SubjectSchema(ma.Schema):
    name       = fields.String(required=True, validate=validate.Length(min=2))
    code       = fields.String(required=False)
    professor  = fields.String(required=False)
    credits    = fields.Integer(required=False)
    difficulty = fields.Integer(required=False, validate=validate.Range(min=1, max=5))
