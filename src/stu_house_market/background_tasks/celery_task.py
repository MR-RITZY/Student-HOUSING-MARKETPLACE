from celery import Celery
from celery.exceptions import TimeoutError
from kombu.exceptions import OperationalError
from contextlib import contextmanager


from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info, app_error


def get_broker_url():
    protocol = "amqps" if settings.ENV == "PROD" else "amqp"
    endpoint = f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
    auth_cred = (
        f"{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}"
        if settings.RABBITMQ_USERNAME and settings.RABBITMQ_PASSWORD
        else ""
    )

    return f"{protocol}://{auth_cred}@{endpoint}//{settings.RABBITMQ_DB}"


def get_backend_url():
    endpoint = f"{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    auth_cred = (
        f"{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}"
        if settings.REDIS_USERNAME and settings.REDIS_PASSWORD
        else ""
    )
    return f"redis://{auth_cred}@{endpoint}//{settings.RABBITMQ_DB}"


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


@contextmanager
def check_celery_worker():
    try:
        inspect = app.control.inspect(timeout=5)
        result = inspect.ping()

        if not result:
            app_error.error("No Celery workers available")
        else:
            workers = list(result.keys())
            app_info.info(f"Celery workers healthy: {workers}")

        yield

    except (TimeoutError, OperationalError) as e:
        app_error.error(f"Celery worker connection failed: {e}")

    except Exception as e:
        app_error.error(f"Unexpected Celery health check error: {e}")
