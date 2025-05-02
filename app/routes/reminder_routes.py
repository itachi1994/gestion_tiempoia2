from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models.task import Task
from app import db

reminder_bp = Blueprint('reminder', __name__)

# Endpoint para obtener las tareas que necesitan un recordatorio
@reminder_bp.route('/task/reminders', methods=['GET'])
@jwt_required()
def get_task_reminders():
    user_id = get_jwt_identity()
    now = datetime.utcnow()

    # Consultar tareas que tengan un recordatorio programado
    reminders = Task.query.filter_by(user_id=user_id).filter(Task.reminder_time <= now).all()

    # Lógica para enviar notificaciones (puede ser correo, push, etc.)
    # En este caso, solo devolveremos las tareas que necesitan recordatorio
    return jsonify([task.serialize() for task in reminders]), 200

# Simulación de un job o cron para enviar recordatorios
def send_reminders():
    now = datetime.utcnow()
    tasks_to_remind = Task.query.filter(Task.reminder_time <= now, Task.status == 'pending').all()

    for task in tasks_to_remind:
        # Aquí es donde enviaríamos el recordatorio (por ejemplo, usando correo)
        send_email_reminder(task)
        task.reminder_time = None  # Limpiar el campo reminder_time una vez que se ha enviado
        db.session.commit()

def send_email_reminder(task):
    # Lógica para enviar el correo (usar Flask-Mail o un servicio de correo)
    print(f"Recordatorio enviado para la tarea {task.title}")
