from django.core.mail.backends.base import BaseEmailBackend


class CeleryEmailBackend(BaseEmailBackend):
    """Queue each email for a Celery worker to send, instead of sending it
    inside the web request.

    SMTP can take tens of seconds, and a web container serves one request at a
    time, so sending inline froze that container (and every request queued
    behind it) for the whole send. The worker delivers through
    ``settings.CELERY_EMAIL_BACKEND``.
    """

    def send_messages(self, email_messages):
        from aiarena.core.tasks import send_email  # tasks imports Celery/Redis; keep that out of import time

        for message in email_messages:
            # The message is pickled onto the queue; its connection (this
            # backend) isn't needed by, and doesn't belong in, the worker.
            message.connection = None
            send_email.delay(message)
        return len(email_messages)
