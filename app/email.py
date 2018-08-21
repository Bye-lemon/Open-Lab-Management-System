from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from . import mail


def async_send_email(app, message):
    with app.app_content():
        mail.send(message)

def send_email(destination, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(app.config['LAB_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                      sender=app.config['LAB_MAIL_SENDER'], recipients=[destination])
    message.body = render_template(template + '.txt', **kwargs)
    thread = Thread(target=async_send_email, args=[app, message])
    thread.start()
    return thread
