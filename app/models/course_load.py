from app import db

class CourseLoad(db.Model):
    __tablename__ = 'course_loads'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id  = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    weekly_hours= db.Column(db.Integer, nullable=False)  # horas deseadas de estudio
    priority    = db.Column(db.Integer, default=3)       # 1‑5
    next_exam   = db.Column(db.Date)

    subject = db.relationship("Subject", backref=db.backref("load", uselist=False))
