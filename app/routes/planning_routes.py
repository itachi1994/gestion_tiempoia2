from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.planning import PlanningPreferences
from app.models.planning_schema import PlanningSchema

planning_bp = Blueprint('planning', __name__)
planning_schema = PlanningSchema()

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
