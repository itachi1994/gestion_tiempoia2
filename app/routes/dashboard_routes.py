from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.task import Task
from app.models.course_load import CourseLoad

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def academic_dashboard():
    user_id = get_jwt_identity()

    # Obtención de las tareas y los cursos relacionados con el usuario
    tasks = Task.query.filter_by(user_id=user_id).all()
    course_loads = CourseLoad.query.filter_by(user_id=user_id).all()

    # Corregir el uso de "courses" y reemplazarlo por "course_loads"
    if not tasks or not course_loads:
        return jsonify({"message": "No hay suficientes datos para generar el panel"}), 400

    course_stats = []
    total_done = 0
    total_tasks = 0

    for course_load in course_loads:
        course_tasks = [t for t in tasks if t.course_load_id == course_load.id]  # Asegurarse de usar el id correcto
        done_tasks = [t for t in course_tasks if t.status == 'done']
        pending_tasks = [t for t in course_tasks if t.status != 'done']

        if course_tasks:
            percent = int((len(done_tasks) / len(course_tasks)) * 100)
        else:
            percent = 0

        course_stats.append({
            "course": course_load.subject.name,  # Usar el nombre de la materia o curso desde course_load
            "total_tasks": len(course_tasks),
            "completed": len(done_tasks),
            "pending": len(pending_tasks),
            "progress": percent
        })

        total_done += len(done_tasks)
        total_tasks += len(course_tasks)

    overall_progress = int((total_done / total_tasks) * 100) if total_tasks else 0

    # Feedback automático
    if overall_progress >= 85:
        level = "Alto"
        advice = "¡Excelente! Sigue así, tu rendimiento es muy alto."
    elif overall_progress >= 60:
        level = "Medio"
        advice = "Vas bien, pero aún puedes mejorar la constancia."
    else:
        level = "Bajo"
        advice = "Te recomendamos organizar mejor tu tiempo de estudio."

    # Devolver la respuesta con los datos generados
    return jsonify({
        "total_courses": len(course_loads),  # Usar "course_loads" en lugar de "courses"
        "overall_progress": overall_progress,
        "performance_level": level,
        "advice": advice,
        "courses": course_stats
    }), 200
