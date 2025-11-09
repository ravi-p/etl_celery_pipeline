# app/celery_app.py
from celery import Celery
from app.config import Config

# Initialize Celery app
celery_app = Celery(
    'etl_pipeline',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)
celery_app.conf.update(

    task_serializer=Config.CELERY_TASK_SERIALIZER,
    result_serializer=Config.CELERY_RESULT_SERIALIZER,
    accept_content=Config.CELERY_ACCEPT_CONTENT,
    timezone=Config.CELERY_TIMEZONE,
    enable_utc=True,
    # Define queues for each worker
    task_queues={
        'gmail_queue': {'exchange': 'gmail_queue', 'routing_key': 'gmail_queue'},
        'parser_queue': {'exchange': 'parser_queue', 'routing_key': 'parser_queue'},
        'db_saver_queue': {'exchange': 'db_saver_queue', 'routing_key': 'db_saver_queue'},
    },
    # Celery Beat Schedule
    beat_schedule={
        'check-gmail-every-1-minutes': {
            'task': 'app.tasks.check_gmail_for_invoices',
            'schedule': 60.0,  # Every 60 seconds (1 minute)
            'options': {'queue': 'gmail_queue'},
        },
    }
)

if __name__ == '__main__':
    celery_app.start()
