from app import ma
from marshmallow import fields, validate

class CourseLoadSchema(ma.Schema):
    subject_id   = fields.Integer(required=True)
    weekly_hours = fields.Integer(required=True, validate=validate.Range(min=1, max=40))
    priority     = fields.Integer(required=False, validate=validate.Range(min=1, max=5))
    next_exam    = fields.Date(required=False)
