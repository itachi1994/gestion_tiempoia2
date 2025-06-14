from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.suggestion import WeeklySuggestion
from app.models.suggestion_schema import SuggestionSchema
from app.models.task import Task
from app.models.habit import StudyHabitSurvey
from app.models.availability import Availability
from datetime import datetime, timedelta

suggestion_bp = Blueprint('suggestion', __name__)
suggestion_schema = SuggestionSchema()
suggestion_list_schema = SuggestionSchema(many=True)

@suggestion_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def generate_weekly_suggestions():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    habit = StudyHabitSurvey.query.filter_by(user_id=user_id).first()
    slots = Availability.query.filter_by(user_id=user_id).all()

    suggestions = []

    today = datetime.utcnow().date()
    upcoming_tasks = [t for t in tasks if t.due_date.date() <= today + timedelta(days=7) and t.status != 'done']

    if upcoming_tasks:
        for task in upcoming_tasks:
            suggestions.append(f"No olvides: '{task.title}' vence el {task.due_date.strftime('%Y-%m-%d')}.")

    if habit:
        if habit.early_bird:
            suggestions.append("Aprovecha las mañanas para estudiar, según tu preferencia.")
        else:
            suggestions.append("Organiza sesiones nocturnas, ya que te concentras mejor de noche.")
        if habit.preferred_block_minutes:
            suggestions.append(f"Divide tus sesiones en bloques de {habit.preferred_block_minutes} minutos.")

    if slots:
        suggestions.append("Distribuye tus tareas en los espacios disponibles que marcaste.")

    suggestion_obj = WeeklySuggestion(
        user_id=user_id,
        content="\n".join(suggestions)
    )
    db.session.add(suggestion_obj)
    db.session.commit()

    return suggestion_schema.jsonify(suggestion_obj), 200
