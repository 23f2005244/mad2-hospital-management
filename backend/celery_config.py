from celery.schedules import crontab
from extensions import celery

def make_celery(app):
    celery.main = app.import_name
    celery.conf.update(
        broker_url='redis://localhost:6379/0',
        result_backend='redis://localhost:6379/0'
    )

    # ─── SCHEDULED TASKS ─────────────────────────────────────────
    celery.conf.beat_schedule = {
        # Daily reminder at 8 AM
        'daily-reminder': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        # Monthly report on 1st of every month at 9 AM
        'monthly-report': {
            'task': 'tasks.send_monthly_reports',
            'schedule': crontab(hour=9, minute=0, day_of_month=1),
        },
    }
    celery.conf.timezone = 'Asia/Kolkata'

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery