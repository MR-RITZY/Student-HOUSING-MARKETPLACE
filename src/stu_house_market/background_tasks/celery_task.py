from celery import Celery
from asgiref.sync import async_to_sync
from typing import Optional, List


from src.stu_house_market.config import settings
from src.stu_house_market.background_tasks.email_sender import send_email

broker_url = (
    f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@"
    f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)

backend_url = (
    f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@"
    f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

app = Celery(
    "stu_house_market",
    broker=broker_url,
    backend=backend_url,
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


def run_async_task_as_sync(func, *args, **kwargs):
    try:
        result = async_to_sync(func)(*args, **kwargs)
        return result
    except Exception as e:
        print(f"Async-to-Sync Task Error: {e}")
        raise


@app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_message(self,
    recipients: List[str],
    subject: str,
    body: Optional[str] = None,
    html_template: Optional[str] = None,
    template_body: Optional[dict] = None,
):
    try:

        return run_async_task_as_sync(
            send_email,
            recipients=recipients,
            subject=subject,
            body=body,
            html_template=html_template,
            template_body=template_body,
        )
    except Exception as e:
        raise self.retry(exc=e)