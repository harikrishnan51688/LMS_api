from main import mail, celery
from flask_mail import Message

@celery.task
def send_email():
  msg = Message(
    'Hello',
    sender='admin@email.com',
    recipients=['recipient@example.com'],
    body='This is a test email sent from Flask-Mail!'
  )
  mail.send(msg)
  return 'Email sent succesfully!'