from extensions import celery, mail
from models.models import db, Appointment, Patient, Doctor, User, Treatment, Department
from flask_mail import Message
from datetime import date, datetime
from flask import current_app
import csv
import io
import requests as http_requests


# ─── HELPER: Send Google Chat Webhook ────────────────────────────
def send_gchat_message(text):
    """Send a message to Google Chat via Webhook. Silently skips if URL not configured."""
    try:
        webhook_url = current_app.config.get('GOOGLE_CHAT_WEBHOOK_URL', '')
    except RuntimeError:
        webhook_url = ''
    if not webhook_url:
        return False
    try:
        resp = http_requests.post(
            webhook_url,
            json={'text': text},
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"Google Chat webhook failed: {e}")
        return False


# ─── TASK 1: DAILY REMINDERS ─────────────────────────────────────
@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Scheduled daily at 8 AM (IST).
    Checks all Booked appointments for today and sends:
      - An email reminder to each patient
      - A Google Chat webhook notification (if configured)
    """
    today = date.today()

    # Get all booked appointments for today
    appointments = Appointment.query.filter_by(
        date=today,
        status='Booked'
    ).all()

    email_sent = 0
    gchat_sent = 0

    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        doctor = Doctor.query.get(appt.doctor_id)
        user = User.query.get(patient.user_id) if patient else None

        if not user or not user.email:
            continue

        doctor_name = doctor.name if doctor else "N/A"
        appt_date = str(appt.date)
        appt_time = appt.time

        # ── Send Email ────────────────────────────────────────
        try:
            msg = Message(
                subject='🏥 Hospital Appointment Reminder',
                recipients=[user.email],
                html=f'''
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #2c7be5;">⏰ Appointment Reminder</h2>
                    <p>Dear <strong>{patient.name}</strong>,</p>
                    <p>This is a reminder that you have an appointment scheduled <strong>today</strong>:</p>
                    <table style="border-collapse: collapse; width: 100%; max-width: 400px;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; background: #f8f9fa;"><strong>Doctor</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">Dr. {doctor_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; background: #f8f9fa;"><strong>Date</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{appt_date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; background: #f8f9fa;"><strong>Time</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{appt_time}</td>
                        </tr>
                    </table>
                    <p style="margin-top: 15px;">Please visit the hospital at the scheduled time.</p>
                    <p style="color: #999; font-size: 12px;">— Hospital Management System</p>
                </body>
                </html>
                '''
            )
            mail.send(msg)
            email_sent += 1
        except Exception as e:
            print(f"Failed to send email reminder to {user.email}: {e}")

        # ── Send Google Chat Webhook ──────────────────────────
        gchat_text = (
            f"🏥 *Appointment Reminder*\n"
            f"Patient: {patient.name}\n"
            f"Doctor: Dr. {doctor_name}\n"
            f"Date: {appt_date}\n"
            f"Time: {appt_time}\n"
            f"Please visit the hospital at the scheduled time."
        )
        if send_gchat_message(gchat_text):
            gchat_sent += 1

    return f"Daily reminders — Emails sent: {email_sent}, Google Chat sent: {gchat_sent}"


# ─── TASK 2: MONTHLY ACTIVITY REPORT ─────────────────────────────
@celery.task(name='tasks.send_monthly_reports')
def send_monthly_reports():
    """
    Scheduled on the 1st of every month at 9 AM (IST).
    For each active doctor, builds an HTML activity report covering the previous
    month's appointments, diagnoses, treatments, and prescriptions, then emails it.
    """
    today = date.today()

    # Determine the previous month
    if today.month == 1:
        report_month = 12
        report_year = today.year - 1
    else:
        report_month = today.month - 1
        report_year = today.year

    import calendar
    month_name = calendar.month_name[report_month]

    doctors = Doctor.query.filter_by(is_active=True).all()
    sent_count = 0

    for doctor in doctors:
        user = User.query.get(doctor.user_id)
        if not user or not user.email:
            continue

        dept = Department.query.get(doctor.department_id)

        # Get appointments for last month
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            db.extract('month', Appointment.date) == report_month,
            db.extract('year', Appointment.date) == report_year
        ).order_by(Appointment.date).all()

        if not appointments:
            continue

        total = len(appointments)
        completed = sum(1 for a in appointments if a.status == 'Completed')
        cancelled = sum(1 for a in appointments if a.status == 'Cancelled')
        booked = sum(1 for a in appointments if a.status == 'Booked')

        # Unique patients
        unique_patients = len(set(a.patient_id for a in appointments))

        # Build appointment detail rows
        rows = ''
        for i, appt in enumerate(appointments, 1):
            patient = Patient.query.get(appt.patient_id)
            treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

            status_color = '#28a745' if appt.status == 'Completed' else (
                '#dc3545' if appt.status == 'Cancelled' else '#007bff'
            )

            rows += f'''
            <tr style="background: {'#f8f9fa' if i % 2 == 0 else 'white'}">
                <td style="padding:8px;border:1px solid #ddd;">{i}</td>
                <td style="padding:8px;border:1px solid #ddd;">{patient.name if patient else "N/A"}</td>
                <td style="padding:8px;border:1px solid #ddd;">{str(appt.date)}</td>
                <td style="padding:8px;border:1px solid #ddd;">{appt.time}</td>
                <td style="padding:8px;border:1px solid #ddd;">
                    <span style="color:{status_color};font-weight:bold;">{appt.status}</span>
                </td>
                <td style="padding:8px;border:1px solid #ddd;">{treatment.diagnosis if treatment else "—"}</td>
                <td style="padding:8px;border:1px solid #ddd;">{treatment.prescription if treatment else "—"}</td>
                <td style="padding:8px;border:1px solid #ddd;">{treatment.medicines if treatment else "—"}</td>
            </tr>
            '''

        html_report = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <div style="max-width: 800px; margin: 0 auto;">
                <div style="background: #2c7be5; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin:0;">📊 Monthly Activity Report</h2>
                    <p style="margin:5px 0 0 0; opacity:0.9;">{month_name} {report_year}</p>
                </div>

                <div style="border:1px solid #ddd; border-top:none; padding: 20px; border-radius: 0 0 8px 8px;">
                    <h3 style="color:#2c7be5;">Doctor Information</h3>
                    <table style="border-collapse:collapse; width:100%; margin-bottom:20px;">
                        <tr>
                            <td style="padding:8px; background:#f8f9fa; border:1px solid #ddd; width:30%;"><strong>Name</strong></td>
                            <td style="padding:8px; border:1px solid #ddd;">Dr. {doctor.name}</td>
                        </tr>
                        <tr>
                            <td style="padding:8px; background:#f8f9fa; border:1px solid #ddd;"><strong>Specialization</strong></td>
                            <td style="padding:8px; border:1px solid #ddd;">{doctor.specialization or "N/A"}</td>
                        </tr>
                        <tr>
                            <td style="padding:8px; background:#f8f9fa; border:1px solid #ddd;"><strong>Department</strong></td>
                            <td style="padding:8px; border:1px solid #ddd;">{dept.name if dept else "N/A"}</td>
                        </tr>
                    </table>

                    <h3 style="color:#2c7be5;">Summary</h3>
                    <table style="border-collapse:collapse; width:100%; margin-bottom:20px;">
                        <tr>
                            <td style="padding:10px; text-align:center; border:1px solid #ddd; background:#e8f4fd;">
                                <strong style="font-size:24px; color:#2c7be5;">{total}</strong><br>
                                <span style="color:#666;">Total Appointments</span>
                            </td>
                            <td style="padding:10px; text-align:center; border:1px solid #ddd; background:#e8fdf0;">
                                <strong style="font-size:24px; color:#28a745;">{completed}</strong><br>
                                <span style="color:#666;">Completed</span>
                            </td>
                            <td style="padding:10px; text-align:center; border:1px solid #ddd; background:#fde8e8;">
                                <strong style="font-size:24px; color:#dc3545;">{cancelled}</strong><br>
                                <span style="color:#666;">Cancelled</span>
                            </td>
                            <td style="padding:10px; text-align:center; border:1px solid #ddd; background:#e8f0fd;">
                                <strong style="font-size:24px; color:#007bff;">{booked}</strong><br>
                                <span style="color:#666;">Pending</span>
                            </td>
                        </tr>
                    </table>
                    <p><strong>Unique Patients Seen:</strong> {unique_patients}</p>

                    <h3 style="color:#2c7be5;">Appointment Details</h3>
                    <table style="border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr style="background: #2c7be5; color: white;">
                                <th style="padding:8px;border:1px solid #ddd;">#</th>
                                <th style="padding:8px;border:1px solid #ddd;">Patient</th>
                                <th style="padding:8px;border:1px solid #ddd;">Date</th>
                                <th style="padding:8px;border:1px solid #ddd;">Time</th>
                                <th style="padding:8px;border:1px solid #ddd;">Status</th>
                                <th style="padding:8px;border:1px solid #ddd;">Diagnosis</th>
                                <th style="padding:8px;border:1px solid #ddd;">Prescription</th>
                                <th style="padding:8px;border:1px solid #ddd;">Medicines</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>

                    <p style="color:#999; margin-top:20px; font-size:12px;">
                        Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M")} — Hospital Management System
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''

        try:
            msg = Message(
                subject=f'📊 Monthly Activity Report — {month_name} {report_year}',
                recipients=[user.email],
                html=html_report
            )
            mail.send(msg)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send report to {user.email}: {e}")

    return f"Monthly reports sent: {sent_count}"


# ─── TASK 3: CSV EXPORT (User Triggered) ─────────────────────────
@celery.task(name='tasks.export_patient_csv')
def export_patient_csv(patient_id, user_email):
    """
    Async job triggered by the patient from their dashboard or history page.
    Builds a CSV of all completed treatments and emails it as an attachment.
    Also sends a Google Chat alert once done (if configured).
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return "Patient not found"

    user = User.query.filter_by(id=patient.user_id).first()

    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    ).order_by(Appointment.date.desc()).all()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'Visit No', 'User ID', 'Username', 'Patient Name', 'Patient ID',
        'Consulting Doctor', 'Department',
        'Appointment Date', 'Appointment Time', 'Visit Type',
        'Diagnosis', 'Prescription', 'Medicines',
        'Tests Done', 'Notes', 'Next Visit Suggested'
    ])

    # Data rows
    for i, appt in enumerate(appointments, 1):
        doctor = Doctor.query.get(appt.doctor_id)
        dept = Department.query.get(doctor.department_id) if doctor else None
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

        writer.writerow([
            i,
            patient.user_id,
            user.username if user else 'N/A',
            patient.name,
            patient.id,
            doctor.name if doctor else 'N/A',
            dept.name if dept else 'N/A',
            str(appt.date),
            appt.time,
            appt.visit_type,
            treatment.diagnosis if treatment else 'N/A',
            treatment.prescription if treatment else 'N/A',
            treatment.medicines if treatment else 'N/A',
            treatment.tests_done if treatment else 'N/A',
            treatment.notes if treatment else 'N/A',
            str(treatment.next_visit) if treatment and treatment.next_visit else 'N/A'
        ])

    csv_content = output.getvalue()

    # Send CSV via email
    try:
        msg = Message(
            subject='📋 Your Treatment History — CSV Export',
            recipients=[user_email],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c7be5;">📋 Treatment History Export</h2>
                <p>Dear <strong>{patient.name}</strong>,</p>
                <p>Your treatment history CSV is attached to this email.</p>
                <p><strong>Total records:</strong> {len(appointments)}</p>
                <p>The file contains details of all your completed visits including
                   consulting doctor, diagnosis, prescription, medicines, and next visit dates.</p>
                <p style="color: #999; font-size: 12px;">— Hospital Management System</p>
            </body>
            </html>
            ''',
        )
        msg.attach(
            f'treatment_history_{patient.name}.csv',
            'text/csv',
            csv_content
        )
        mail.send(msg)
    except Exception as e:
        return f"Export failed: {e}"

    # Send Google Chat alert once done
    send_gchat_message(
        f"✅ *CSV Export Complete*\n"
        f"Patient: {patient.name}\n"
        f"Records exported: {len(appointments)}\n"
        f"Email sent to: {user_email}"
    )

    return f"CSV exported and sent to {user_email} ({len(appointments)} records)"


# ─── TASK 4: EXPORT ALL DOCTORS CSV (Admin Triggered) ────────────
@celery.task(name='tasks.export_all_doctors_csv')
def export_all_doctors_csv(admin_email):
    """
    Async job triggered by admin from the dashboard.
    Builds a CSV of all doctors with their details and emails it as an attachment.
    """
    doctors = Doctor.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Doctor ID', 'Name', 'Specialization', 'Department',
        'Experience (Years)', 'Qualification', 'Email', 'Active'
    ])

    for d in doctors:
        user = User.query.get(d.user_id)
        dept = Department.query.get(d.department_id) if d.department_id else None
        writer.writerow([
            d.id,
            d.name,
            d.specialization or 'N/A',
            dept.name if dept else 'N/A',
            d.experience_years or 'N/A',
            d.qualification or 'N/A',
            user.email if user else 'N/A',
            'Yes' if d.is_active else 'No'
        ])

    csv_content = output.getvalue()

    try:
        msg = Message(
            subject='Doctors List — CSV Export',
            recipients=[admin_email],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c7be5;">Doctors List Export</h2>
                <p>The doctors list CSV is attached to this email.</p>
                <p><strong>Total doctors:</strong> {len(doctors)}</p>
                <p style="color: #999; font-size: 12px;">— Hospital Management System</p>
            </body>
            </html>
            ''',
        )
        msg.attach(
            'doctors_list.csv',
            'text/csv',
            csv_content
        )
        mail.send(msg)
    except Exception as e:
        return f"Export failed: {e}"

    return f"Doctors CSV exported and sent to {admin_email} ({len(doctors)} records)"