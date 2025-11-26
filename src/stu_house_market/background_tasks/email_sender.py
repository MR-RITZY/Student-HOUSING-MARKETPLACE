from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pathlib import Path
from typing import List, Optional

from src.stu_house_market.config import settings

TEMPLATE_FOLDER = Path(__file__).parent.parent / "static"

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)


mail = FastMail(mail_config)


async def send_email(
    recipients: List[str],
    subject: str,
    body: Optional[str] = None,
    html_template: Optional[str] = None,
    template_body: Optional[dict] = None,
):

    if html_template and (TEMPLATE_FOLDER / html_template).exists():
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_body or {},
            subtype=MessageType.html,
        )
        await mail.send_message(message, template_name=html_template)
        return "sent"

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.plain,
    )
    await mail.send_message(message)

    return "sent"
