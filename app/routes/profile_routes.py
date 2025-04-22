from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_profile_schema import UserProfileSchema
from app import db
from app.extensions import db, bcrypt

profile_bp = Blueprint('profile', __name__)
profile_schema = UserProfileSchema()

@profile_bp.route('/profile', methods=['POST', 'PUT'])
@jwt_required()
def manage_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()
    
    # Validación
    errors = profile_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Crear o actualizar perfil
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        # Crear nuevo perfil
        profile = UserProfile(user_id=current_user_id)
        db.session.add(profile)
    
    # Actualizar datos
    profile.full_name = data['full_name']
    profile.university = data['university']
    profile.academic_program = data['academic_program']
    profile.current_semester = data['current_semester']
    
    if 'enrollment_number' in data:
        profile.enrollment_number = data['enrollment_number']
    if 'phone' in data:
        profile.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        "message": "Perfil actualizado exitosamente",
        "profile": profile_schema.dump(profile)
    }), 200 if request.method == 'PUT' else 201