from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.course_load import CourseLoad
from app.models.course_load_schema import CourseLoadSchema
from app.models.subject import Subject

load_bp = Blueprint('load', __name__)
load_schema = CourseLoadSchema()
load_many  = CourseLoadSchema(many=True)

@load_bp.route('/load', methods=['POST'])
@jwt_required()
def set_load():
    user_id = get_jwt_identity()
    data = request.get_json()
    errors = load_schema.validate(data)
    if errors: return jsonify(errors),400

    # Verifica que la materia pertenezca al usuario
    subj = Subject.query.filter_by(id=data['subject_id'], user_id=user_id).first()
    if not subj:
        return jsonify({"message":"Subject not found"}),404

    cl = CourseLoad.query.filter_by(user_id=user_id, subject_id=subj.id).first()
    if cl:
        # actualiza
        for k,v in data.items(): setattr(cl,k,v)
    else:
        cl = CourseLoad(user_id=user_id, **data)
        db.session.add(cl)
    db.session.commit()
    return load_schema.jsonify(cl), 200

@load_bp.route('/load', methods=['GET'])
@jwt_required()
def list_load():
    user_id = get_jwt_identity()
    loads = CourseLoad.query.filter_by(user_id=user_id).all()
    return load_many.jsonify(loads)
