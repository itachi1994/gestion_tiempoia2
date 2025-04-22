from app import db
from datetime import time

class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)        # e.g. "Monday"
    start_time = db.Column(db.Time, nullable=False)               # 08:00
    end_time   = db.Column(db.Time, nullable=False)               # 10:00

    user = db.relationship("User", backref=db.backref("availabilities", cascade="all,delete"))
