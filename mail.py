from main import mail, celery, db
from flask_mail import Message
from smtplib import SMTPException
from flask import render_template
from datetime import datetime, timedelta
from models import BorrowBook, RequestBook, ReturnBook, User, Rating, Section, Ebook
import requests
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env.secret')

GCHAT_KEY = os.getenv("GCHAT_KEY")

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
    requests.post(f'https://chat.googleapis.com/v1/spaces/AAAAIJz-aVM/messages?key={GCHAT_KEY}&token=hgaPCT2OoBlrGcM1Zrp9bjGTkUDvlIkrLJcbSrzmqFM', 
                  json={'text':f'*{email}* the book "*{title}*" due date on *{due_date}*'})
    return 'Success'
  except SMTPException as e:
    return f'Failed {e}'
  
@celery.task
def send_monthly_report():
  last_thirty_days = datetime.now() - timedelta(days=30)

  borrow_count = db.session.query(BorrowBook).filter(BorrowBook.release_date > last_thirty_days).count()
  request_count = db.session.query(RequestBook).count()
  return_count = db.session.query(ReturnBook).filter(ReturnBook.return_date > last_thirty_days).count()
  active_users = db.session.query(User).filter(User.last_activity > last_thirty_days).count()
  sections_created = db.session.query(Section).filter(Section.created_at > last_thirty_days).count()
  ebook_added = db.session.query(Ebook).filter(Ebook.created_at > last_thirty_days).count()
  ratings_count = db.session.query(Rating).filter(Rating.created_at > last_thirty_days).count()

  data = {'borrow_count':borrow_count, 'request_count':request_count, 'return_count':return_count, 'active_users':active_users, 
          'sections_created':sections_created, 'ebook_added':ebook_added, 'ratings_count':ratings_count}

  msg = Message(
    'Monthly Library report',
    sender='system@lms.com',
    recipients=['admin@email.com'],
  )
  msg.html = render_template('mail-template.html', data=data)
  try:
    mail.send(msg)
    return 'Success'
  except SMTPException as e:
    return f'Failed {e}'