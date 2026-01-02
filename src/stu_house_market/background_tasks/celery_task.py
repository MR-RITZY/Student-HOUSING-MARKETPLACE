"""from celery import Celery
from asgiref.sync import async_to_sync
import resend
from typing import List, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


from src.stu_house_market.core.config import settings


broker_url = (
    f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@"
    f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)

backend_url = (
    f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@"
    f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

app = Celery(
    "stu_house_market background_task worker",
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


static_path = Path(__file__).parent.parent / "static"

env = Environment(loader=FileSystemLoader(static_path))
resend.api_key = settings.RESEND_API_KEY

@app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email(
    self,
    recipients: List[str],
    subject: str,
    text: Optional[str] = None,
    template_rel_path: Optional[str] = None,
    template_data: Optional[dict] = None,
):
    try:
        html = None

        template_abs_path = static_path / template_rel_path

        if template_rel_path and template_abs_path.exists():
            if template_data is not None:
                html = render_template(template_rel_path, template_data)
            else:
                html = template_abs_path.read_text()

        
        params: resend.Emails.SendParams = {
            "from": settings.MAIL_FROM,
            "to": recipients,
            "subject": subject,
            "html": html,
            "text": text,
        }

        email = resend.Emails.send(params)
        return "sent"
    except Exception as e:
        raise self.retry(exc=e)


def render_template(file_name: str, data: dict):
    try:
        template = env.get_template(file_name)
        return template.render(data or {})
    except Exception:
        return None



"""