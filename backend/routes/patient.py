from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Doctor, Patient, Appointment, Department, Treatment, DoctorAvailability
from functools import wraps
from datetime import datetime, date, timedelta
import json

def get_cache():
    from extensions import cache
    return cache

patient_bp = Blueprint('patient', __name__)

# ─── PATIENT REQUIRED DECORATOR ──────────────────────────────────
def patient_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user = json.loads(get_jwt_identity())
        if current_user['role'] != 'patient':
            return jsonify({'message': 'Patient access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


# ─── GET PATIENT PROFILE ──────────────────────────────────────────
@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    user = User.query.get(current_user['id'])
    return jsonify({
        'id': patient.id,
        'name': patient.name,
        'username': user.username,
        'email': user.email,
        'age': patient.age,
        'gender': patient.gender,
        'phone': patient.phone,
        'address': patient.address,
        'blood_group': patient.blood_group
    }), 200


# ─── UPDATE PATIENT PROFILE ───────────────────────────────────────
@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
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
    return jsonify({'message': 'Profile updated successfully'}), 200


# ─── PATIENT DASHBOARD ────────────────────────────────────────────
@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def dashboard():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    today = date.today()

    # Upcoming appointments
    upcoming = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Booked'
    ).filter(Appointment.date >= today).all()

    # Past appointments
    past = Appointment.query.filter_by(
        patient_id=patient.id
    ).filter(
        (Appointment.status == 'Completed') |
        (Appointment.status == 'Cancelled')
    ).all()

    # All departments
    departments = Department.query.all()
    dept_list = [{'id': d.id, 'name': d.name, 'description': d.description} for d in departments]

    upcoming_list = []
    for a in upcoming:
        doctor = Doctor.query.get(a.doctor_id)
        dept = Department.query.get(doctor.department_id) if doctor else None
        upcoming_list.append({
            'id': a.id,
            'doctor_name': doctor.name if doctor else None,
            'department': dept.name if dept else None,
            'date': str(a.date),
            'time': a.time,
            'status': a.status
        })

    return jsonify({
        'patient_name': patient.name,
        'upcoming_appointments': upcoming_list,
        'total_upcoming': len(upcoming),
        'total_past': len(past),
        'departments': dept_list
    }), 200


# ─── GET ALL DEPARTMENTS ──────────────────────────────────────────
@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    cache_key = 'all_departments'
    cached = get_cache().get(cache_key)
    if cached:
        return jsonify(cached), 200

    departments = Department.query.all()
    result = []
    for dept in departments:
        doctors = Doctor.query.filter_by(
            department_id=dept.id,
            is_active=True
        ).all()
        result.append({
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctor_count': len(doctors)
        })
    get_cache().set(cache_key, result, timeout=300)
    return jsonify(result), 200

# ─── GET DOCTORS BY DEPARTMENT ────────────────────────────────────
@patient_bp.route('/departments/<int:dept_id>/doctors', methods=['GET'])
@patient_required
def get_doctors_by_department(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'message': 'Department not found'}), 404

    doctors = Doctor.query.filter_by(
        department_id=dept_id,
        is_active=True
    ).all()

    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'name': d.name,
            'specialization': d.specialization,
            'experience_years': d.experience_years,
            'qualification': d.qualification
        })
    return jsonify({'department': dept.name, 'doctors': result}), 200


# ─── SEARCH DOCTORS ───────────────────────────────────────────────
@patient_bp.route('/search/doctors', methods=['GET'])
@patient_required
def search_doctors():
    query = request.args.get('q', '')
    doctors = Doctor.query.filter(
        (Doctor.name.ilike(f'%{query}%')) |
        (Doctor.specialization.ilike(f'%{query}%'))
    ).filter_by(is_active=True).all()

    result = []
    for d in doctors:
        dept = Department.query.get(d.department_id)
        result.append({
            'id': d.id,
            'name': d.name,
            'specialization': d.specialization,
            'department': dept.name if dept else None,
            'experience_years': d.experience_years,
            'qualification': d.qualification
        })
    return jsonify(result), 200


# ─── GET DOCTOR AVAILABILITY ──────────────────────────────────────
@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@patient_required
def get_doctor_availability(doctor_id):
    cache_key = f'doctor_availability_{doctor_id}'
    cached = get_cache().get(cache_key)
    if cached:
        return jsonify(cached), 200

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    today = date.today()
    week_later = today + timedelta(days=7)

    slots = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).order_by(DoctorAvailability.date).all()

    dept = Department.query.get(doctor.department_id)
    result = []
    for slot in slots:
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=slot.date,
            time=slot.start_time,
            status='Booked'
        ).first()
        result.append({
            'id': slot.id,
            'date': str(slot.date),
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'slot_type': slot.slot_type,
            'is_booked': existing is not None
        })

    data = {
        'doctor': {
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization,
            'department': dept.name if dept else None,
            'experience_years': doctor.experience_years,
            'qualification': doctor.qualification
        },
        'availability': result
    }
    get_cache().set(cache_key, data, timeout=60)
    return jsonify(data), 200


# ─── BOOK APPOINTMENT ─────────────────────────────────────────────
@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    data = request.get_json()
    required = ['doctor_id', 'date', 'time']
    for field in required:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    # Check doctor exists
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    # Parse date
    appt_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    # Prevent double booking - same doctor, date, time
    existing = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        date=appt_date,
        time=data['time'],
        status='Booked'
    ).first()
    if existing:
        return jsonify({'message': 'This slot is already booked'}), 400

    # Prevent patient double booking same date time
    patient_existing = Appointment.query.filter_by(
        patient_id=patient.id,
        date=appt_date,
        time=data['time'],
        status='Booked'
    ).first()
    if patient_existing:
        return jsonify({'message': 'You already have an appointment at this time'}), 400

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=data['doctor_id'],
        date=appt_date,
        time=data['time'],
        status='Booked',
        visit_type=data.get('visit_type', 'In-person')
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        'message': 'Appointment booked successfully',
        'appointment_id': appointment.id
    }), 201


# ─── GET PATIENT APPOINTMENTS ─────────────────────────────────────
@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    appointments = Appointment.query.filter_by(
        patient_id=patient.id
    ).order_by(Appointment.date.desc()).all()

    result = []
    for a in appointments:
        doctor = Doctor.query.get(a.doctor_id)
        dept = Department.query.get(doctor.department_id) if doctor else None
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            'id': a.id,
            'doctor_name': doctor.name if doctor else None,
            'department': dept.name if dept else None,
            'date': str(a.date),
            'time': a.time,
            'status': a.status,
            'visit_type': a.visit_type,
            'treatment': {
                'diagnosis': treatment.diagnosis,
                'prescription': treatment.prescription,
                'notes': treatment.notes,
                'tests_done': treatment.tests_done,
                'medicines': treatment.medicines,
                'next_visit': str(treatment.next_visit) if treatment.next_visit else None
            } if treatment else None
        })
    return jsonify(result), 200


# ─── CANCEL APPOINTMENT ───────────────────────────────────────────
@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@patient_required
def cancel_appointment(appointment_id):
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.patient_id != patient.id:
        return jsonify({'message': 'Unauthorized'}), 403

    if appointment.status != 'Booked':
        return jsonify({'message': 'Only booked appointments can be cancelled'}), 400

    appointment.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled successfully'}), 200


# ─── GET PATIENT HISTORY ──────────────────────────────────────────
@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_history():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    completed = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Completed'
    ).order_by(Appointment.date.desc()).all()

    result = []
    for a in completed:
        doctor = Doctor.query.get(a.doctor_id)
        dept = Department.query.get(doctor.department_id) if doctor else None
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            'appointment_id': a.id,
            'doctor_name': doctor.name if doctor else None,
            'department': dept.name if dept else None,
            'date': str(a.date),
            'time': a.time,
            'visit_type': a.visit_type,
            'treatment': {
                'diagnosis': treatment.diagnosis,
                'prescription': treatment.prescription,
                'notes': treatment.notes,
                'tests_done': treatment.tests_done,
                'medicines': treatment.medicines,
                'next_visit': str(treatment.next_visit) if treatment.next_visit else None
            } if treatment else None
        })
    return jsonify(result), 200

# ─── TRIGGER CSV EXPORT ───────────────────────────────────────────
@patient_bp.route('/export-csv', methods=['POST'])
@patient_required
def trigger_csv_export():
    current_user = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    user = User.query.get(current_user['id'])

    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Trigger async celery task
    from tasks import export_patient_csv
    task = export_patient_csv.delay(patient.id, user.email)

    return jsonify({
        'message': 'CSV export started. You will receive an email shortly.',
        'task_id': task.id
    }), 200