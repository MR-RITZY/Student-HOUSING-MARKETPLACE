from pika import ConnectionParameters, BlockingConnection, PlainCredentials, SSLOptions
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import ssl
from contextlib import contextmanager

from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info, app_error



@contextmanager
def check_broker():
    """
    Attempts to establish a connection to RabbitMQ.
    Relies on Pika's internal retry mechanism.
    Raises an exception if the broker is unreachable.
    """

    credentials = PlainCredentials(
        username=settings.RABBITMQ_USERNAME,
        password=settings.RABBITMQ_PASSWORD,
    )

    ssl_options = None
    if settings.ENV == "PROD":
        ssl_context = ssl.create_default_context()
        ssl_options = SSLOptions(
            context=ssl_context,
            server_hostname=settings.RABBITMQ_HOST,
        )

    connection_params = ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=credentials,
        ssl_options=ssl_options,
        heartbeat=60,
        blocked_connection_timeout=300,
        connection_attempts=5,
        retry_delay=3,
        socket_timeout=30.0,
        channel_max=3,
    )

    try:
        connection = BlockingConnection(connection_params)
        if connection.is_open:
            app_info.info("RabbitMQ Connection Successful.")
            connection.close()
        yield
    except (AMQPConnectionError, AMQPChannelError) as exc:
        app_error.critical(f"Failed to Connect to RabbitMQ: {exc}")
        raise
