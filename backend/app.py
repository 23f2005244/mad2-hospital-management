from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from extensions import mail, cache, celery

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_import()

    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080", "http://localhost:8081"]}})
    mail.init_app(app)
    cache.init_app(app)

    from celery_config import make_celery
    make_celery(app)

    # Ensure Celery tasks are registered
    import tasks

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    with app.app_context():
        db.create_all()
        seed_data()

    return app, celery

def db_import():
    global db
    from models.models import db as _db
    globals()['db'] = _db

from models.models import db

def seed_data():
    from models.models import User, Department
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)

    departments = ['Cardiology', 'Oncology', 'General', 'Neurology', 'Orthopedics']
    for dept_name in departments:
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            dept = Department(
                name=dept_name,
                description=f'Department of {dept_name}'
            )
            db.session.add(dept)

    db.session.commit()
    print("Database seeded successfully!")

app, celery = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)