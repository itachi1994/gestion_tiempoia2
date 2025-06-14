from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.planning import PlanningPreferences
from app.models.planning_schema import PlanningSchema
from app.models.task import Task
from app.models.habit import StudyHabitSurvey
from app.models.availability import Availability
from datetime import datetime, timedelta
from app.utils.deepseek_api import generate_schedule_with_deepseek
from app.models.user_schedule import UserSchedule
from app.models.user_schedule_schema import UserScheduleSchema
import json
import os
import requests

planning_bp = Blueprint('planning', __name__)
planning_schema = PlanningSchema()
user_schedule_schema = UserScheduleSchema()
user_schedule_many_schema = UserScheduleSchema(many=True)

def serialize_habit(habit):
    if not habit:
        return None
    return {
        "preferred_block_minutes": habit.preferred_block_minutes,
        "early_bird": habit.early_bird,
        "distractions": habit.distractions,
        "study_location": habit.study_location
    }

def serialize_prefs(prefs):
    if not prefs:
        return None
    return {
        "max_daily_hours": prefs.max_daily_hours,
        "preferred_days": prefs.preferred_days,
        "rest_days": prefs.rest_days
    }

def build_deepseek_prompt(tasks, availability, prefs, habit):
    # Simplifica los datos para el prompt
    task_list = [
        {
            "title": t.title,
            "due_date": t.due_date.strftime("%Y-%m-%d") if t.due_date else None,
            "priority": t.priority,
        } for t in tasks
    ]
    avail_list = [a.serialize() for a in availability]
    prefs_dict = {
        "max_daily_hours": prefs.max_daily_hours if prefs else 4,
        "preferred_days": prefs.preferred_days if prefs else "Monday,Tuesday,Wednesday,Thursday,Friday",
        "rest_days": prefs.rest_days if prefs else "Sunday"
    }
    habit_dict = {
        "preferred_block_minutes": habit.preferred_block_minutes if habit else 50,
        "early_bird": habit.early_bird if habit else True,
        "distractions": habit.distractions if habit else "",
        "study_location": habit.study_location if habit else ""
    }
    prompt = (
        "Eres un asistente que organiza horarios de estudio. "
        "Con base en las siguientes tareas, disponibilidad, preferencias y hábitos, "
        "genera un horario semanal en formato JSON, donde cada día tiene una lista de bloques con tareas asignadas. "
        "Ejemplo de formato: {\"Monday\": [{\"task_id\": 1, \"title\": \"Tarea X\", \"block\": \"08:00-10:00\"}], ...}\n\n"
        f"Tareas: {json.dumps(task_list, ensure_ascii=False)}\n"
        f"Disponibilidad: {json.dumps(avail_list, ensure_ascii=False)}\n"
        f"Preferencias: {json.dumps(prefs_dict, ensure_ascii=False)}\n"
        f"Hábitos: {json.dumps(habit_dict, ensure_ascii=False)}"
    )
    return prompt

def call_deepseek_api(prompt):
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Eres un asistente que ayuda a organizar horarios de estudio."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    # DeepSeek responde con un string, intenta extraer el JSON
    content = response.json()["choices"][0]["message"]["content"]
    try:
        # Busca el primer bloque JSON en la respuesta
        start = content.find('{')
        end = content.rfind('}') + 1
        schedule_json = content[start:end]
        schedule = json.loads(schedule_json)
    except Exception:
        schedule = {}
    return schedule

@planning_bp.route('/planning', methods=['POST', 'PUT'])
@jwt_required()
def create_or_update_planning():
    user_id = get_jwt_identity()
    data = request.get_json()
    errors = planning_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    prefs = PlanningPreferences.query.filter_by(user_id=user_id).first()
    if prefs:
        for k, v in data.items(): setattr(prefs, k, v)
    else:
        prefs = PlanningPreferences(user_id=user_id, **data)
        db.session.add(prefs)

    db.session.commit()
    return planning_schema.jsonify(prefs), 200

@planning_bp.route('/planning', methods=['GET'])
@jwt_required()
def get_planning():
    user_id = get_jwt_identity()
    prefs = PlanningPreferences.query.filter_by(user_id=user_id).first()
    if not prefs:
        return jsonify({"message": "No preferences found"}), 404
    return planning_schema.jsonify(prefs), 200

@planning_bp.route('/planning/data', methods=['GET'])
@jwt_required()
def get_planning_data():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    habit = StudyHabitSurvey.query.filter_by(user_id=user_id).first()
    availability = Availability.query.filter_by(user_id=user_id).all()
    course_loads = CourseLoad.query.filter_by(user_id=user_id).all()
    prefs = PlanningPreferences.query.filter_by(user_id=user_id).first()

    return jsonify({
        "tasks": [t.serialize() if hasattr(t, 'serialize') else {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else None,
            "priority": t.priority,
            "status": t.status,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else None,
            "course_load_id": t.course_load_id,
            "subjects_id": t.subjects_id
        } for t in tasks],
        "habit": serialize_habit(habit),
        "availability": [a.serialize() for a in availability],
        "course_loads": [{
            "id": cl.id,
            "subject_id": cl.subject_id,
            "weekly_hours": cl.weekly_hours,
            "priority": cl.priority,
            "next_exam": str(cl.next_exam) if cl.next_exam else None
        } for cl in course_loads],
        "planning_preferences": serialize_prefs(prefs)
    }), 200

@planning_bp.route('/planning/schedule', methods=['GET'])
@jwt_required()
def generate_schedule():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id, status='pending').order_by(Task.due_date.asc()).all()
    habit = StudyHabitSurvey.query.filter_by(user_id=user_id).first()
    availability = Availability.query.filter_by(user_id=user_id).all()
    prefs = PlanningPreferences.query.filter_by(user_id=user_id).first()

    if not tasks or not availability:
        return jsonify({"schedule": {}, "message": "No hay tareas o disponibilidad configurada"}), 200

    prompt = build_deepseek_prompt(tasks, availability, prefs, habit)
    try:
        schedule = call_deepseek_api(prompt)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 402:
            return jsonify({"schedule": {}, "error": "No tienes crédito suficiente o acceso en DeepSeek. Revisa tu cuenta o clave de API."}), 402
        return jsonify({"schedule": {}, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"schedule": {}, "error": str(e)}), 500
    return jsonify({"schedule": schedule}), 200

@planning_bp.route('/planning/schedule', methods=['POST'])
@jwt_required()
def save_schedule():
    user_id = get_jwt_identity()
    data = request.get_json()
    schedule = data.get("schedule")
    if not schedule:
        return jsonify({"error": "No schedule provided"}), 400

    # Guarda el horario como string JSON
    schedule_obj = UserSchedule(user_id=user_id, schedule_json=json.dumps(schedule))
    db.session.add(schedule_obj)
    db.session.commit()
    return user_schedule_schema.jsonify(schedule_obj), 201

@planning_bp.route('/planning/schedule/history', methods=['GET'])
@jwt_required()
def get_schedule_history():
    user_id = get_jwt_identity()
    schedules = UserSchedule.query.filter_by(user_id=user_id).order_by(UserSchedule.created_at.desc()).all()
    return user_schedule_many_schema.jsonify(schedules), 200

# --- INTEGRACIÓN CON EL SISTEMA ---
# 1. El frontend debe hacer una petición GET a /api/planning/schedule con el token JWT.
# 2. El backend responde con el horario sugerido en formato JSON.
# 3. El frontend puede mostrar el horario en un calendario, tabla o lista.
# 4. Si deseas guardar el horario generado, puedes crear un nuevo modelo (por ejemplo, UserSchedule)
#    y un endpoint POST para almacenar el resultado en la base de datos.
# 5. Si el usuario quiere modificar el horario, puedes permitirle editarlo y luego guardar los cambios.
# 5. Si el usuario quiere modificar el horario, puedes permitirle editarlo y luego guardar los cambios.
