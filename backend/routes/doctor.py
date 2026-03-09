from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Doctor, Patient, Appointment, Department, Treatment, DoctorAvailability
from functools import wraps
from datetime import datetime, date, timedelta
import json

def get_cache():
    from extensions import cache
    return cache

doctor_bp = Blueprint('doctor', __name__)

# ─── DOCTOR REQUIRED DECORATOR ───────────────────────────────────
def doctor_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user = json.loads(get_jwt_identity())
        if current_user['role'] != 'doctor':
            return jsonify({'message': 'Doctor access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


# ─── GET DOCTOR PROFILE ───────────────────────────────────────────
@doctor_bp.route('/profile', methods=['GET'])
@doctor_required
def get_profile():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    dept = Department.query.get(doctor.department_id)
    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'specialization': doctor.specialization,
        'department': dept.name if dept else None,
        'department_id': doctor.department_id,
        'experience_years': doctor.experience_years,
        'qualification': doctor.qualification,
        'is_active': doctor.is_active
    }), 200


# ─── DOCTOR DASHBOARD ─────────────────────────────────────────────
@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    today = date.today()
    week_later = today + timedelta(days=7)

    # Upcoming appointments for today
    today_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status='Booked'
    ).filter(Appointment.date == today).all()

    # Upcoming appointments for the week
    week_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status='Booked'
    ).filter(
        Appointment.date >= today,
        Appointment.date <= week_later
    ).all()

    # All assigned patients
    patient_ids = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=doctor.id
    ).distinct().all()
    total_patients = len(patient_ids)

    return jsonify({
        'doctor_name': doctor.name,
        'today_appointments': len(today_appointments),
        'week_appointments': len(week_appointments),
        'total_patients': total_patients
    }), 200


# ─── GET DOCTOR APPOINTMENTS ──────────────────────────────────────
@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    # Optional filter by date
    filter_date = request.args.get('date')
    query = Appointment.query.filter_by(doctor_id=doctor.id)

    if filter_date:
        query = query.filter(Appointment.date == filter_date)

    appointments = query.order_by(Appointment.date, Appointment.time).all()

    result = []
    for a in appointments:
        patient = Patient.query.get(a.patient_id)
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': patient.name if patient else None,
            'patient_age': patient.age if patient else None,
            'patient_gender': patient.gender if patient else None,
            'date': str(a.date),
            'time': a.time,
            'status': a.status,
            'visit_type': a.visit_type,
            'has_treatment': treatment is not None
        })
    return jsonify(result), 200


# ─── UPDATE APPOINTMENT STATUS ────────────────────────────────────
@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@doctor_required
def update_appointment_status(appointment_id):
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.doctor_id != doctor.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['Completed', 'Cancelled']:
        return jsonify({'message': 'Status must be Completed or Cancelled'}), 400

    appointment.status = new_status
    db.session.commit()

    return jsonify({'message': f'Appointment marked as {new_status}'}), 200


# ─── GET ASSIGNED PATIENTS ────────────────────────────────────────
@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    # Get unique patients who have appointments with this doctor
    patient_ids = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=doctor.id
    ).distinct().all()

    result = []
    for (pid,) in patient_ids:
        patient = Patient.query.get(pid)
        if patient:
            user = User.query.get(patient.user_id)
            last_appointment = Appointment.query.filter_by(
                doctor_id=doctor.id,
                patient_id=pid
            ).order_by(Appointment.date.desc()).first()

            result.append({
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
                'phone': patient.phone,
                'blood_group': patient.blood_group,
                'email': user.email if user else None,
                'last_appointment': str(last_appointment.date) if last_appointment else None,
                'last_status': last_appointment.status if last_appointment else None
            })
    return jsonify(result), 200


# ─── GET PATIENT HISTORY ──────────────────────────────────────────
@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient_id
    ).order_by(Appointment.date.desc()).all()

    result = []
    for a in appointments:
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            'appointment_id': a.id,
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

    return jsonify({
        'patient': {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'phone': patient.phone,
            'blood_group': patient.blood_group
        },
        'history': result
    }), 200


# ─── ADD / UPDATE TREATMENT ───────────────────────────────────────
@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST'])
@doctor_required
def add_treatment(appointment_id):
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.doctor_id != doctor.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()

    # Check if treatment already exists
    treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()

    if treatment:
        # Update existing treatment
        treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
        treatment.prescription = data.get('prescription', treatment.prescription)
        treatment.notes = data.get('notes', treatment.notes)
        treatment.tests_done = data.get('tests_done', treatment.tests_done)
        treatment.medicines = data.get('medicines', treatment.medicines)
        if data.get('next_visit'):
            treatment.next_visit = datetime.strptime(
                data['next_visit'], '%Y-%m-%d'
            ).date()
    else:
        # Create new treatment
        treatment = Treatment(
            appointment_id=appointment_id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            tests_done=data.get('tests_done'),
            medicines=data.get('medicines')
        )
        if data.get('next_visit'):
            treatment.next_visit = datetime.strptime(
                data['next_visit'], '%Y-%m-%d'
            ).date()
        db.session.add(treatment)

    # Mark appointment as completed
    appointment.status = 'Completed'
    db.session.commit()

    return jsonify({'message': 'Treatment saved successfully'}), 200


# ─── SET AVAILABILITY ─────────────────────────────────────────────
@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.get_json()
    availabilities = data.get('availabilities', [])

    # Delete existing future availability
    today = date.today()
    DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today
    ).delete()

    # Add new availability
    for slot in availabilities:
        avail = DoctorAvailability(
            doctor_id=doctor.id,
            date=datetime.strptime(slot['date'], '%Y-%m-%d').date(),
            start_time=slot['start_time'],
            end_time=slot['end_time'],
            slot_type=slot.get('slot_type', 'morning')
        )
        db.session.add(avail)

    db.session.commit()
    get_cache().delete(f'doctor_availability_{doctor.id}')
    return jsonify({'message': 'Availability updated successfully'}), 200


# ─── GET AVAILABILITY ─────────────────────────────────────────────
@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    current_user = json.loads(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    cache_key = f'doctor_availability_{doctor.id}'
    cached = get_cache().get(cache_key)
    if cached:
        return jsonify(cached), 200

    today = date.today()
    week_later = today + timedelta(days=7)

    slots = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).order_by(DoctorAvailability.date).all()

    result = []
    for slot in slots:
        result.append({
            'id': slot.id,
            'date': str(slot.date),
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'slot_type': slot.slot_type
        })

    get_cache().set(cache_key, result, timeout=60)
    return jsonify(result), 200