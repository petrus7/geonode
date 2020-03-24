from geonode.celery_app import app
from django.conf import settings
from user_messages.models import Message, Thread
from user_messages.signals import message_sent


@app.task(queue='email')
def notify_thread_participants(thread_id, message_id):
    email_template = 'user_messages/email/email_new_message'
    message = Message.objects.get(pk=message_id)
    thread = Thread.objects.get(pk=thread_id)
    msg_sender = message.sender
    users = thread.registered_users
    groups = thread.registered_groups
    ctx = {
        'message': message.content,
        'thread_subject': thread.subject,
        'sender': message.sender,
        'thread_url': settings.SITEURL + thread.get_absolute_url()[1:],
        'logo_url': f'{settings.SITEURL}static/img/logo_ihp_alpha_small.png'
    }
    for group in groups:
        users |= group.user_set.all().distinct()

    users = users.exclude(pk=msg_sender.pk)
    for user in users:
        user.send_mail(email_template, ctx)


def notify_thread_participants_wrap(**kwargs):
    thread = kwargs.get('thread').pk
    message = kwargs.get('message').pk
    notify_thread_participants.delay(thread_id=thread, message_id=message)


def initialize_notification_signal():
    message_sent.connect(
        notify_thread_participants_wrap,
        sender=Message
    )
