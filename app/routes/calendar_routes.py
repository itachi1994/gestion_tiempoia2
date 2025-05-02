from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.availability import Availability
from app.models.task import Task
from app import db

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar/fullweek', methods=['GET'])
@jwt_required()
def get_full_week_view():
    user_id = get_jwt_identity()

    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())
    dates = [(start_of_week + timedelta(days=i)).date() for i in range(7)]

    response = {}

    for date in dates:
        day_start = datetime.combine(date, datetime.min.time())
        day_end   = datetime.combine(date, datetime.max.time())

        availability = Availability.query.filter(
            Availability.user_id == user_id,
            Availability.start_time >= day_start,
            Availability.end_time <= day_end
        ).all()

        tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.due_date >= day_start,
            Task.due_date <= day_end
        ).all()

        response[str(date)] = {
            "availability": [a.serialize() for a in availability],
            "tasks": [t.serialize() for t in tasks],
            "recommendations": generate_recommendations(availability, tasks)
        }

    return jsonify(response)

def generate_recommendations(availability, tasks):
    recs = []
    now = datetime.utcnow()

    if len(availability) == 0:
        recs.append("Considera agendar tiempo de estudio")

    if tasks:
        recs.append("Prioriza tareas según fecha de entrega")

        urgent_tasks = [t for t in tasks if (t.due_date - now).total_seconds() <= 172800 and not t.completed]
        if urgent_tasks:
            recs.append(f"Tienes {len(urgent_tasks)} tarea(s) con vencimiento en menos de 48 horas")

    if len(tasks) > 3:
        recs.append("Aplica técnica Pomodoro para avanzar")

    return recs

