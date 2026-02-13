from celery import Celery


from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info


def get_broker_url():
    if settings.ENV == "PROD":
        return (
            f"amqps://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//{settings.RABBITMQ_DB}"
        )
    return (
        f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@"
        f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
    )


def get_backend_url():
    if settings.ENV == "PROD":
        return (
            f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}"
            f"@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"


app = Celery(
    "stu_house_market background_task worker",
    broker=get_broker_url(),
    backend=get_backend_url(),
    include=["src.stu_house_market.background_tasks.celery_task"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    result_expires=3600,
)


def background_task_sender(task_name: str, task_data: dict):
    app_info.info(f"Sending Background: {task_name}")
    app.send_task(task_name, kwargs=task_data)
    app_info.info("Task sent")