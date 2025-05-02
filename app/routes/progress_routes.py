from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task import Task
from app.models.course_load import CourseLoad  # Cambio aquí, usando CourseLoad en lugar de Course
from app.models.progress import ProgressReport
from app.models.progress_schema import ProgressReportSchema
from datetime import datetime, timedelta

progress_bp = Blueprint('progress', __name__)
progress_schema = ProgressReportSchema()

@progress_bp.route('/progress', methods=['POST'])
@jwt_required()
def generate_progress_report():
    user_id = get_jwt_identity()
    data = request.get_json()
    period = data.get('period', 'weekly')

    if period not in ['weekly', 'monthly']:
        return jsonify({"error": "Invalid period"}), 400

    now = datetime.utcnow()
    since = now - timedelta(days=7 if period == 'weekly' else 30)

    tasks = Task.query.filter(Task.user_id == user_id, Task.created_at >= since).all()
    
    # Ajustado para usar CourseLoad en lugar de Course
    course_loads = CourseLoad.query.filter_by(user_id=user_id).all()

    done = [t for t in tasks if t.status == 'done']
    pending = [t for t in tasks if t.status != 'done']

    report_lines = [
        f"Resumen {period}:",
        f"- Tareas completadas: {len(done)}",
        f"- Tareas pendientes: {len(pending)}"
    ]

    for course_load in course_loads:
        # Relacionar las tareas con el course_load adecuado
        course_tasks = [t for t in tasks if t.course_load_id == course_load.id]
        if course_tasks:
            done_count = sum(1 for t in course_tasks if t.status == 'done')
            percent = int((done_count / len(course_tasks)) * 100)
            report_lines.append(f"- {course_load.subject.name}: {percent}% completado")  # Asumiendo que 'subject' es una relación de CourseLoad

    if len(done) == 0:
        report_lines.append(" Consejo: intenta completar al menos una tarea al día para mantener el ritmo.")
    elif len(done) < len(pending):
        report_lines.append(" Consejo: prioriza tareas con fechas próximas y mantén constancia.")

    final_report = "\n".join(report_lines)

    progress = ProgressReport(user_id=user_id, period=period, report=final_report)
    db.session.add(progress)
    db.session.commit()

    return progress_schema.jsonify(progress), 200
