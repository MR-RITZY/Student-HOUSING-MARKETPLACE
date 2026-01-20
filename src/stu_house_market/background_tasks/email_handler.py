from src.stu_house_market.utils.safe_token import get_safe_token

from src.stu_house_market.core.config import settings
from src.stu_house_market.background_tasks.celery_task import background_task_sender


def verification_mail_sender(user_data: dict):
    token = get_safe_token({'user_id': user_data['user_id']})
    verification_link = f"{settings.BASE_URL}/user/verify?token={token}"
    html_data = {'user_firstname': user_data['firstname'], 'link': verification_link}
    mail_data = {
        'recipients': [user_data['email']],
        'subject': 'Account Vefication',
        'template_path': 'verify-new-account.html',
        'template_data': html_data
    }
    background_task_sender('email_sender', mail_data)