from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.habit import StudyHabitSurvey
from app.models.task import Task
from app.models.course_load import CourseLoad

tips_bp = Blueprint('tips', __name__)

@tips_bp.route('/tips', methods=['GET'])
@jwt_required()
def get_personalized_tips():
    user_id = get_jwt_identity()

    habits = StudyHabitSurvey.query.filter_by(user_id=user_id).first()
    tasks = Task.query.filter_by(user_id=user_id).all()
    course_loads = CourseLoad.query.filter_by(user_id=user_id).all()

    if not tasks or not course_loads:
        return jsonify({"message": "Faltan datos para generar recomendaciones"}), 400

    total_tasks = len(tasks)
    done_tasks = len([t for t in tasks if t.status == 'done'])
    progress = int((done_tasks / total_tasks) * 100) if total_tasks else 0

    tips = []

    # Basado en hábitos
    if habits:
        if habits.early_bird:
            tips.append("Aprovecha tus mañanas: agenda lo más difícil temprano.")
        else:
            tips.append("Estudia temas complejos en la tarde/noche cuando estás más activo.")

        if habits.preferred_block_minutes <= 45:
            tips.append("Haz pausas frecuentes, ideal cada {} minutos.".format(habits.preferred_block_minutes))
        else:
            tips.append("Considera dividir tus bloques largos con descansos breves.")

        if habits.study_location:
            tips.append(f"Prueba alternar tu espacio de estudio. Actualmente usas: {habits.study_location}.")

        if habits.distractions:
            tips.append(f"Minimiza distracciones como: {habits.distractions}.")

    # Basado en rendimiento
    if progress < 60:
        tips.append("Revisa tus tareas pendientes. Comienza con las más fáciles para ganar ritmo.")
    elif progress < 85:
        tips.append("Vas bien. Usa técnica Pomodoro para mantener consistencia.")
    else:
        tips.append("¡Excelente ritmo! Mantén tu estrategia y no olvides recompensarte.")

    # Carga académica
    if len(course_loads) >= 5:
        tips.append("Tu carga académica es alta. Prioriza tareas por fecha de entrega.")
    elif len(course_loads) <= 2:
        tips.append("Aprovecha el tiempo extra para profundizar en temas clave o adelantar trabajos.")

    return jsonify({
        "tips": tips,
        "progreso_actual": progress,
        "cursos": len(course_loads)
    }), 200

