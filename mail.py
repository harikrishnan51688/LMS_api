from main import mail, celery
from flask_mail import Message
from smtplib import SMTPException
from flask import render_template


@celery.task
def send_email():
  msg = Message(
    'Hello',
    sender='admin@email.com',
    recipients=['recipient@example.com'],
  )
  # msg.body = render_template('template.html')
  msg.html = render_template('mail-template.html')
  try:
    mail.send(msg)
    return 'Success'
  except SMTPException as e:
    return f'Failed {e}'
  


@celery.task
def send_remainder(email, title, due_date):
  msg = Message(
    f'Remainder: Due date {title}',
    sender='admin@email.com',
    recipients=[email],
    body=f'This is a remainder mail for borrowed book "{title}" which is appearing due date on {due_date}. Return book manually or it will auto expiry after due date'
  )
  try:
    mail.send(msg)
    return 'Success'
  except SMTPException as e:
    return f'Failed {e}'
  