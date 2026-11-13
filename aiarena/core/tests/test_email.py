import pickle
from unittest import mock

from django.core import mail
from django.core.mail import EmailMultiAlternatives

from aiarena.core.email import CeleryEmailBackend
from aiarena.core.tasks import send_email


def _message():
    message = EmailMultiAlternatives("Subject", "text body", "from@example.com", ["to@example.com"])
    message.attach_alternative("<p>html body</p>", "text/html")
    return message


def test_backend_queues_each_message_instead_of_sending():
    messages = [_message(), _message()]
    with mock.patch("aiarena.core.tasks.send_email.delay") as delay:
        sent = CeleryEmailBackend().send_messages(messages)

    assert sent == 2
    assert [call.args[0] for call in delay.call_args_list] == messages
    assert mail.outbox == []  # nothing was sent from the request


def test_queued_message_survives_the_pickle_round_trip_to_the_worker(settings):
    """The task queue pickles messages (CELERY_TASK_SERIALIZER), so a message
    queued by the backend must still pickle once the backend has let go of it."""
    settings.CELERY_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    message = _message()
    message.connection = CeleryEmailBackend()
    with mock.patch("aiarena.core.tasks.send_email.delay") as delay:
        CeleryEmailBackend().send_messages([message])

    send_email(pickle.loads(pickle.dumps(delay.call_args.args[0])))

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Subject"
    assert mail.outbox[0].alternatives == [("<p>html body</p>", "text/html")]


def test_task_sends_through_the_configured_real_backend(settings):
    settings.CELERY_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    send_email(_message())

    assert [m.to for m in mail.outbox] == [["to@example.com"]]
