from main import celery
from celery.schedules import crontab
import csv
from zipfile import ZipFile, ZIP_DEFLATED
import os
from models import RequestBook, BorrowBook, ReturnBook, User
from datetime import datetime, timedelta
from mail import send_remainder, send_monthly_report


@celery.task
def generate_csv(user_id):
    folder_path = os.path.join(os.getcwd(), f'static/csv/{user_id}')
    os.makedirs(folder_path, exist_ok=True)

    file_path_borrow = os.path.join(os.getcwd(), f'static/csv/{user_id}/borrow.csv')
    with open(file_path_borrow, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id','borrow_id','book_id','release_date','due_date','book_title','auto_expiry'])
        borrow_records = BorrowBook.query.filter_by(user_id=user_id).all()
        for b in borrow_records:
            writer.writerow([b.user_id, b.borrow_id, b.book_id, b.release_date, b.due_date, b.ebook.title, b.auto_expiry])

    file_path_request = os.path.join(os.getcwd(), f'static/csv/{user_id}/request.csv')
    with open(file_path_request, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id','request_id','book_id','book_title'])
        request_records = RequestBook.query.filter_by(user_id=user_id).all()
        for r in request_records:
            writer.writerow([r.user_id, r.request_id, r.book_id, r.ebook.title])
    
    file_path_return = os.path.join(os.getcwd(), f'static/csv/{user_id}/return.csv')
    with open(file_path_return, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id','return_id','book_id','return_date','book_title'])
        return_records = ReturnBook.query.filter_by(user_id=user_id).all()
        for r in return_records:
            writer.writerow([r.user_id, r.return_id, r.book_id, r.return_date, r.ebook.title])

    zip_path = os.path.join(os.getcwd(), f'static/csv/{user_id}/zipped_data.zip')
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.csv'):
                    # Create the full file path
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder_path)
                    zipf.write(file_path, arcname)

    return zip_path

@celery.task
def expiry_remainder():
    b = BorrowBook.query.all()
    for book in b:
        if book.auto_expiry and (book.due_date - datetime.now()) < timedelta(days=8):
            send_remainder.delay(email=book.user.email, title=book.ebook.title, due_date=book.due_date)

    

# run task every 10 sec
@celery.on_after_configure.connect
def book_expiry_remainder(sender, **kwargs):
    sender.add_periodic_task(10, expiry_remainder.s(), name='remainder')

@celery.on_after_configure.connect
def monthly_report(sender, **kwargs):
    sender.add_periodic_task(10, send_monthly_report.s(), name='monthly_report')