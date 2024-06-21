from main import celery
from celery.schedules import crontab
import csv
import os
from models import RequestBook, BorrowBook, ReturnBook, User
from datetime import datetime, timedelta
from mail import send_remainder


@celery.task
def generate_csv(user_id):
    file_path = os.path.join(os.getcwd(), f'static/csv/{user_id}.csv')
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id','borrow_id','book_id','release_date','due_date','book_title','auto_expiry'])
        borrow_records = BorrowBook.query.filter_by(user_id=user_id).all()
        for b in borrow_records:
            writer.writerow([b.user_id, b.borrow_id, b.book_id, b.release_date, b.due_date, b.ebook.title, b.auto_expiry])
    return file_path


@celery.task
def remainder():
    b = BorrowBook.query.all()
    for book in b:
        if book.auto_expiry and (book.due_date - datetime.now()) < timedelta(days=8):
            send_remainder.delay(email=book.user.email, title=book.ebook.title, due_date=book.due_date)

    

# # run task every 10 sec
@celery.on_after_configure.connect
def hello(sender, **kwargs):
    sender.add_periodic_task(10, remainder.s(), name='remainder')

