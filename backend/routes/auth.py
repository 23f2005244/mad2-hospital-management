import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.models import db, User, Patient, Doctor
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# ─── PATIENT REGISTER ───────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    required = ['username', 'email', 'password', 'name']
    for field in required:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    # Create User
    user = User(
        username=data['username'],
        email=data['email'],
        role='patient'
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    # Create Patient profile
    patient = Patient(
        user_id=user.id,
        name=data['name'],
        age=data.get('age'),
        gender=data.get('gender'),
        phone=data.get('phone'),
        address=data.get('address'),
        blood_group=data.get('blood_group')
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'message': 'Patient registered successfully'}), 201


# ─── LOGIN (All roles) ───────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    if user.is_blacklisted:
        return jsonify({'message': 'Your account has been blacklisted'}), 403

    # Create JWT token with user info
    import json
    access_token = create_access_token(identity=json.dumps({
        'id': user.id,
        'username': user.username,
        'role': user.role
    }))

    # Get profile id based on role
    profile_id = None
    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            profile_id = doctor.id
    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            profile_id = patient.id

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_id': profile_id
        }
    }), 200


# ─── GET CURRENT USER ────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user = json.loads(get_jwt_identity())
    user = User.query.get(current_user['id'])

    if not user:
        return jsonify({'message': 'User not found'}), 404

    profile_id = None
    extra = {}

    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            profile_id = doctor.id
            extra = {
                'name': doctor.name,
                'specialization': doctor.specialization,
                'experience_years': doctor.experience_years
            }
    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            profile_id = patient.id
            extra = {
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
                'phone': patient.phone
            }

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'profile_id': profile_id,
        **extra
    }), 200


# ─── CHANGE PASSWORD ─────────────────────────────────────────────
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user = json.loads(get_jwt_identity())
    data = request.get_json()

    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': 'Old and new password required'}), 400

    user = User.query.get(current_user['id'])

    if not user.check_password(data['old_password']):
        return jsonify({'message': 'Old password is incorrect'}), 401

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200