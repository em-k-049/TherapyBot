from celery import Celery

# Celery instance
celery = Celery(
    "therapybot",
    broker="redis://localhost:6379/0",   # Redis broker
    backend="redis://localhost:6379/0"   # Redis backend
)

# Optional config
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Example task (you can add more later)
@celery.task(name="app.tasks.celery_app.example_task")
def example_task(message: str):
    return f"Processed message: {message}"
