import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Doctor, Patient, Appointment, Department, Treatment
from werkzeug.security import generate_password_hash
from functools import wraps

def get_cache():
    from extensions import cache
    return cache

admin_bp = Blueprint('admin', __name__)

# ─── ADMIN REQUIRED DECORATOR ────────────────────────────────────
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        import json
        current_user = json.loads(get_jwt_identity())
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# ─── TRIGGER DAILY REMINDERS (ADMIN ACTION) ─────────────────────
@admin_bp.route('/send-daily-reminders', methods=['POST'])
@admin_required
def trigger_daily_reminders():
    try:
        from tasks import send_daily_reminders
        result = send_daily_reminders.delay()
        return jsonify({'message': 'Daily reminders task started.', 'task_id': result.id}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to start daily reminders: {str(e)}'}), 500


# ─── TRIGGER MONTHLY REPORT (ADMIN ACTION) ───────────────────────
@admin_bp.route('/send-monthly-report', methods=['POST'])
@admin_required
def trigger_monthly_report():
    try:
        from tasks import send_monthly_reports
        result = send_monthly_reports.delay()
        return jsonify({'message': 'Monthly report task started.', 'task_id': result.id}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to start monthly report: {str(e)}'}), 500


# ─── EXPORT DOCTORS CSV (ADMIN ACTION) ───────────────────────────
@admin_bp.route('/export-doctors-csv', methods=['POST'])
@admin_required
def export_doctors_csv():
    try:
        from tasks import export_all_doctors_csv
        current_user = json.loads(get_jwt_identity())
        user = User.query.get(current_user['id'])
        result = export_all_doctors_csv.delay(user.email)
        return jsonify({'message': 'Doctors CSV export started. You will receive an email shortly.', 'task_id': result.id}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to start CSV export: {str(e)}'}), 500


# ─── DASHBOARD STATS ─────────────────────────────────────────────
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    cache_key = 'admin_dashboard_stats'
    cached = get_cache().get(cache_key)
    if cached:
        return jsonify(cached), 200

    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status='Booked').count()
    completed = Appointment.query.filter_by(status='Completed').count()
    cancelled = Appointment.query.filter_by(status='Cancelled').count()

    data = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'booked_appointments': booked,
        'completed_appointments': completed,
        'cancelled_appointments': cancelled
    }
    get_cache().set(cache_key, data, timeout=60)
    return jsonify(data), 200


# ─── GET ALL DOCTORS ──────────────────────────────────────────────
@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    cache_key = 'admin_all_doctors'
    cached = get_cache().get(cache_key)
    if cached:
        return jsonify(cached), 200

    doctors = Doctor.query.all()
    result = []
    for d in doctors:
        user = User.query.get(d.user_id)
        dept = Department.query.get(d.department_id)
        result.append({
            'id': d.id,
            'user_id': d.user_id,
            'name': d.name,
            'username': user.username if user else None,
            'email': user.email if user else None,
            'specialization': d.specialization,
            'department': dept.name if dept else None,
            'department_id': d.department_id,
            'experience_years': d.experience_years,
            'qualification': d.qualification,
            'is_active': d.is_active,
            'is_blacklisted': user.is_blacklisted if user else False
        })
    get_cache().set(cache_key, result, timeout=120)
    return jsonify(result), 200


# ─── ADD DOCTOR ───────────────────────────────────────────────────
@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    data = request.get_json()

    required = ['username', 'email', 'password', 'name', 'specialization']
    for field in required:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        role='doctor'
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    # Create doctor profile
    doctor = Doctor(
        user_id=user.id,
        name=data['name'],
        specialization=data['specialization'],
        department_id=data.get('department_id'),
        experience_years=data.get('experience_years'),
        qualification=data.get('qualification')
    )
    db.session.add(doctor)
    db.session.commit()

    get_cache().delete('admin_all_doctors')
    get_cache().delete('admin_dashboard_stats')

    return jsonify({'message': 'Doctor added successfully', 'doctor_id': doctor.id}), 201


# ─── UPDATE DOCTOR ────────────────────────────────────────────────
@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.get_json()
    user = User.query.get(doctor.user_id)

    # Update doctor fields
    if 'name' in data:
        doctor.name = data['name']
    if 'specialization' in data:
        doctor.specialization = data['specialization']
    if 'department_id' in data:
        doctor.department_id = data['department_id']
    if 'experience_years' in data:
        doctor.experience_years = data['experience_years']
    if 'qualification' in data:
        doctor.qualification = data['qualification']
    if 'is_active' in data:
        doctor.is_active = data['is_active']

    # Update user fields
    if 'email' in data and user:
        user.email = data['email']
    if 'password' in data and user:
        user.set_password(data['password'])

    db.session.commit()

    get_cache().delete('admin_all_doctors')
    get_cache().delete('admin_dashboard_stats')

    return jsonify({'message': 'Doctor updated successfully'}), 200


# ─── DELETE DOCTOR ────────────────────────────────────────────────
@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    user = User.query.get(doctor.user_id)
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()

    get_cache().delete('admin_all_doctors')
    get_cache().delete('admin_dashboard_stats')

    return jsonify({'message': 'Doctor deleted successfully'}), 200


# ─── BLACKLIST DOCTOR ─────────────────────────────────────────────
@admin_bp.route('/doctors/<int:doctor_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    user = User.query.get(doctor.user_id)
    if user:
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
        status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
        get_cache().delete('admin_all_doctors')
        get_cache().delete('admin_dashboard_stats')
        return jsonify({'message': f'Doctor {status} successfully'}), 200

    return jsonify({'message': 'User not found'}), 404


# ─── GET ALL PATIENTS ─────────────────────────────────────────────
@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    patients = Patient.query.all()
    result = []
    for p in patients:
        user = User.query.get(p.user_id)
        result.append({
            'id': p.id,
            'user_id': p.user_id,
            'name': p.name,
            'username': user.username if user else None,
            'email': user.email if user else None,
            'age': p.age,
            'gender': p.gender,
            'phone': p.phone,
            'address': p.address,
            'blood_group': p.blood_group,
            'is_blacklisted': user.is_blacklisted if user else False
        })
    return jsonify(result), 200


# ─── BLACKLIST PATIENT ────────────────────────────────────────────
@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    user = User.query.get(patient.user_id)
    if user:
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
        status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
        return jsonify({'message': f'Patient {status} successfully'}), 200

    return jsonify({'message': 'User not found'}), 404


# ─── UPDATE PATIENT ───────────────────────────────────────────────
@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    data = request.get_json()
    if 'name' in data:
        patient.name = data['name']
    if 'age' in data:
        patient.age = data['age']
    if 'gender' in data:
        patient.gender = data['gender']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'address' in data:
        patient.address = data['address']
    if 'blood_group' in data:
        patient.blood_group = data['blood_group']

    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'}), 200


# ─── GET ALL APPOINTMENTS ─────────────────────────────────────────
@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    appointments = Appointment.query.all()
    result = []
    for a in appointments:
        patient = Patient.query.get(a.patient_id)
        doctor = Doctor.query.get(a.doctor_id)
        dept = Department.query.get(doctor.department_id) if doctor else None
        result.append({
            'id': a.id,
            'patient_name': patient.name if patient else None,
            'patient_id': a.patient_id,
            'doctor_name': doctor.name if doctor else None,
            'doctor_id': a.doctor_id,
            'department': dept.name if dept else None,
            'date': str(a.date),
            'time': a.time,
            'status': a.status,
            'visit_type': a.visit_type
        })
    return jsonify(result), 200


# ─── SEARCH DOCTORS ───────────────────────────────────────────────
@admin_bp.route('/search/doctors', methods=['GET'])
@admin_required
def search_doctors():
    query = request.args.get('q', '')
    doctors = Doctor.query.filter(
        (Doctor.name.ilike(f'%{query}%')) |
        (Doctor.specialization.ilike(f'%{query}%'))
    ).all()

    result = []
    for d in doctors:
        user = User.query.get(d.user_id)
        dept = Department.query.get(d.department_id)
        result.append({
            'id': d.id,
            'name': d.name,
            'username': user.username if user else None,
            'specialization': d.specialization,
            'department': dept.name if dept else None,
            'experience_years': d.experience_years,
            'qualification': d.qualification
        })
    return jsonify(result), 200


# ─── SEARCH PATIENTS ──────────────────────────────────────────────
@admin_bp.route('/search/patients', methods=['GET'])
@admin_required
def search_patients():
    query = request.args.get('q', '')
    patients = Patient.query.filter(
        (Patient.name.ilike(f'%{query}%')) |
        (Patient.phone.ilike(f'%{query}%'))
    ).all()

    result = []
    for p in patients:
        user = User.query.get(p.user_id)
        result.append({
            'id': p.id,
            'name': p.name,
            'username': user.username if user else None,
            'email': user.email if user else None,
            'phone': p.phone,
            'age': p.age,
            'gender': p.gender
        })
    return jsonify(result), 200


# ─── GET ALL DEPARTMENTS ──────────────────────────────────────────
@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    departments = Department.query.all()
    result = []
    for dept in departments:
        doctor_count = Doctor.query.filter_by(
            department_id=dept.id,
            is_active=True
        ).count()
        result.append({
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctor_count': doctor_count
        })
    return jsonify(result), 200


# ─── GET SINGLE DOCTOR ────────────────────────────────────────────
@admin_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@admin_required
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    user = User.query.get(doctor.user_id)
    dept = Department.query.get(doctor.department_id)

    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'username': user.username if user else None,
        'email': user.email if user else None,
        'specialization': doctor.specialization,
        'department': dept.name if dept else None,
        'department_id': doctor.department_id,
        'experience_years': doctor.experience_years,
        'qualification': doctor.qualification,
        'is_active': doctor.is_active
    }), 200