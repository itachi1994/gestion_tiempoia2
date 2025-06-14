from flask_mail import Message
from app.extensions import mail, db 
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))
    due_date = db.Column(db.DateTime)
    reminder_date = db.Column(db.DateTime, nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subjects_id = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates="tasks")

    @staticmethod
    def send_email_reminder(recipient_email, subject, body):
        msg = Message(subject,
                      sender="your_email@example.com",
                      recipients=[recipient_email])
        msg.body = body
        try:
            mail.send(msg)
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Error sending email: {e}")

    @staticmethod
    def send_task_reminders():
        tasks = Task.query.filter(Task.reminder_date <= datetime.now(), Task.status == "pending").all()

        for task in tasks:
            if task.reminder_sent:
                continue

            subject = f"Recordatorio: {task.title}"
            body = f"¡Hola! No olvides completar la tarea: {task.title}.\n\nDescripción: {task.description}\nFecha de vencimiento: {task.due_date.strftime('%Y-%m-%d')}"
            
            Task.send_email_reminder(task.user.email, subject, body)

            task.reminder_sent = True
            db.session.commit()
            task.reminder_sent = True
            db.session.commit()
