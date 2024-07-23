from flask import request, jsonify
from flask_restful import Resource, fields, marshal_with, marshal
from models import Ebook, User, Section, BorrowBook, RequestBook, ReturnBook, Rating, Purchase
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
from datetime import timedelta
from functools import wraps
import os
from sqlalchemy.sql import func, desc, not_, or_
from flask_caching import Cache
from config import config
from models import db
from flask import current_app as app
from celery.result import AsyncResult

cache = Cache()

secret_key = config['default'].SECRET_KEY

# In days
BOOK_EXPIRY_TIME = 7 

def is_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message":"Token is missing!"})
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
            if current_user:
                current_user.last_activity = datetime.datetime.now()
                db.session.commit()
        except:
            return jsonify({"message":"Token is invalid"})
        return f(current_user, *args, **kwargs)
    return decorated

def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message":"Token is missing!"})
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
            if not current_user.role_id == 1:
                return jsonify({'message': "Permission denied"})
        except:
            return jsonify({"message":"Token is invalid"})
        return f(current_user, *args, **kwargs)
    return decorated

def get_time():
    current_time = datetime.datetime.now()
    return current_time.replace(microsecond=0)

# ---------- API for charts ------------- #

class Chart_Sections(Resource):
    def get(self):
        data = Section.query.all()
        # print([d.section_name for d in data])
        # print([len(d.ebook) for d in data])
        chart_data = {
        'labels': [d.section_name for d in data],  # assuming 'id' is a suitable label
        'datasets': [
            {
                'label': 'Books',
                'data': [len(d.ebook) for d in data],  # replace 'your_field' with the actual field you want to display
                'backgroundColor': ['rgba(65, 192, 12, 0.2)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)','rgba(154, 245, 140)'],
                'borderWidth': 1,
                # 'hoverBorderColor': "red",
                'hoverBorderWidth': 2,
                # 'hoverBackgroundColor': 'rgba(154, 245, 140)',
                'pointHoverRadius': 5,
                'borderColor': 'white',
                'tension': 0.1,
                'borderWidth': 2,
            }
          ]
        }
        options = {
            'scales': {
                'y': {
                    'beginAtZero': True
                }
            }
        }
        response_data = {
            'chart_data': chart_data,
            'options': options
        }

        return jsonify(response_data)

class UserJoinChart(Resource):
    def get(self):
        # Query to get the count of users joined per day
        result = db.session.query(func.date(User.date).label('date'), func.count(User.id).label('count')).group_by(func.date(User.date)).order_by(desc(User.date)).limit(7)

        labels = [str(row.date) for row in result]
        data = [row.count for row in result]
        
        # Reverse the labels
        labels = list(reversed(labels))
        # Reverse the data
        data = list(reversed(data))

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Users Joined Last Week',
                    'data': data,
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 2,
                    'fill': False
                }
            ]
        }

        options = {
            'scales': {
                'xAxes': [{
                    'type': 'time',
                    'time': {
                        'unit': 'day',
                        'displayFormats': {
                            'day': 'MMM D'
                        }
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Date'
                    }
                }],
                'y': {
                    'beginAtZero': True,
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Number of Users'
                    }
                }
            },
        }

        response_data = {
            'chart_data': chart_data,
            'options': options
        }

        return jsonify(response_data)


 # ---------------- API for Section --------------------- #
book_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'author': fields.String,
    'subtitle': fields.String,
    'pages': fields.Integer,
    'price': fields.Float,
    'genre': fields.String,
    'file': fields.String,
    'image': fields.String,
    'created_at': fields.DateTime,
}
section_fields = {
    'section_id': fields.Integer,
    'section_name': fields.String,
}

class Sections_(Resource):
    @cache.cached(timeout=60, key_prefix="sections")
    def get(self):
        sections = Section.query.all()
        result = []
        for section in sections:
            s = {
                'section_id': section.section_id,
                'section_name': section.section_name,
                'created_at': section.created_at,
                'book_count': len(section.ebook)
            }
            result.append(s)
        return jsonify({'sections': result})
    
class GetSection_byId(Resource):
    def get(self, section_id):
        section = Section.query.filter_by(section_id=section_id).first()
        if not section:
            return jsonify({"message":"section doesn't exists!"}), 404
        else:
            ebooks = section.ebook
            ebook_list = marshal(ebooks, book_fields)
            data = {'section_id': section.section_id, 'section_name': section.section_name, 'books': ebook_list}
            return data

class Create_Section(Resource):
    @is_admin
    def post(current_user, self):
        name = request.form.get('section_name')
        section = Section(section_name=name)
        try:
            db.session.add(section)
            db.session.commit()
            cache.delete("sections")
            return jsonify({"message":"section added successfully!", 'status': 'success'})
        except:
            return jsonify({"message":"some error occurred", 'status': 'error'})


class Update_Section(Resource):
    @is_admin
    def put(current_user, self, section_id):
        name = request.form.get('section_name')
        section = Section.query.filter_by(section_id=section_id).first()
        if not section:
            return jsonify({"message":"section doesn't exists!"})
        try:
            section.section_name = name
            db.session.add(section)
            db.session.commit()
            cache.delete("sections")
            return jsonify({"message":"section updated successfully!"})
        except:
            return jsonify({"message":"some error occurred"})


class Delete_Section_(Resource):
    @is_admin
    def delete(current_user, self, section_id):
        section = Section.query.filter_by(section_id=section_id).first()
        if not section:
            return jsonify({"message":"section doesn't exists!"})
        try:
            db.session.delete(section)
            db.session.commit()
            cache.delete("sections")
            return jsonify({"message":"section deleted successfully!"})
        except:
            return jsonify({"message":"some error occurred. section not deleted."})




 # ---------------- API for Books --------------------- #
    
class Delete_Ebook(Resource):
    @is_admin
    def delete(current_user,self):
        book_id = request.args.get('book_id')
        book = Ebook.query.filter_by(id=book_id).first()
        if not book:
            return jsonify({"message":"Book doesn't exists!"})
        try:
            db.session.delete(book)
            db.session.commit()
            cache.delete('books')
            cache.delete('sections')
            return jsonify({"message":"Book deleted succussfully", 'status': 'success'})
        except:
            return jsonify({"message":"Some error occurred", 'status': 'error'})


class Update_Ebook(Resource):
    @is_admin
    def put(current_user,self,book_id):

        book = Ebook.query.filter_by(id=book_id).first()
        if not book:
            return jsonify({"message":"Book doesn't exsists!"})
        book.title =    request.form.get('title')
        book.subtitle = request.form.get('subtitle')
        book.genre =    request.form.get('genre')
        book.pages =    request.form.get('pages')
        book.author =   request.form.get('author')
        book.price =    request.form.get('price')

        # for pdf
        try:
            pdf = request.files['file']
            filename = secure_filename(pdf.filename)
            file_path_pdf = (os.path.join(app.root_path, 'static/uploads/pdf/', filename))
            pdf.save(file_path_pdf)    
            book.file = f"uploads/pdf/{filename}"
        except:
            None
        # for cover image
        try:
            image = request.files['image']
            imagename = secure_filename(image.filename)
            file_path_image = (os.path.join(app.root_path, 'static/uploads/images/', imagename))
            image.save(file_path_image)    
            book.image = f"uploads/images/{imagename}"
        except:
            None
        try:
            db.session.add(book)
            db.session.commit()
            cache.delete('books')
        except:
            return jsonify({"message":"Some error occurred!"})

        return jsonify({"message":"Book updated successfully!", "status": 'success'})

class Create_Ebook(Resource):
    @is_admin
    def post(current_user, self):
        try:
            book = Ebook(owner_id=current_user.id, author=request.form.get('author'), title=request.form.get('title'), subtitle=request.form.get('subtitle'), pages=request.form.get('pages'), price=request.form.get('price'), genre=request.form.get('genre'))
            # for pdf
            pdf = request.files['file']
            filename = secure_filename(pdf.filename)
            file_path_pdf = (os.path.join(app.root_path, 'static/uploads/pdf/', filename))
            pdf.save(file_path_pdf)    
            book.file = f"uploads/pdf/{filename}"

            # for cover image
            image = request.files['image']
            imagename = secure_filename(image.filename)
            file_path_image = (os.path.join(app.root_path, 'static/uploads/images/', imagename))
            image.save(file_path_image)    
            book.image = f"uploads/images/{imagename}"

            db.session.add(book)
            db.session.commit()
            cache.delete('books')
            return jsonify({"message":"Book added succussfully", 'status': 'success'})
        except:
            return jsonify({"message":"some error occured", 'status': 'error'})

        
def make_cache_key(*args, **kwargs):
    return f"ebook_{args[0]}"

class Ebook_Byid(Resource):
    @classmethod
    @cache.memoize(30)
    def get(cls, book_id):
        book = Ebook.query.filter_by(id=book_id).first()
        if not book:
            return jsonify({"message":"Book does not exists"})
        json_ebook = {}
        json_ebook["id"] = book.id
        json_ebook["author"] = book.author
        json_ebook["title"] = book.title
        json_ebook["subtitle"] = book.subtitle
        json_ebook["pages"] = book.pages
        json_ebook["price"] = book.price
        json_ebook["genre"] = book.genre
        json_ebook["file"] = book.file
        json_ebook["image"] = book.image
        json_ebook["created_at"] = book.created_at
        json_ebook["avg_rating"] = book.average_rating()
        return jsonify({"book":json_ebook})

class Ebook_(Resource):
    @cache.cached(key_prefix="books", timeout=60)
    def get(self):
        ebooks = Ebook.query.all()
        books_data = []
        bookwith_rating = []
        for book in ebooks:
            book_data = {
                'id': book.id,
                'author': book.author,
                'title': book.title,
                'subtitle': book.subtitle,
                'pages': book.pages,
                'price': book.price,
                'genre': book.genre,
                'file': book.file,
                'image': book.image,
                'created_at': book.created_at,
                'sections': [section.section_name for section in book.sections]
            }
            books_data.append(book_data)

        avg_ratings = db.session.query(Rating.book_id, func.avg(Rating.rating).label('average_rating')).group_by(Rating.book_id).order_by(func.avg(Rating.rating).desc()).all()
        for book_id, avg_rating in avg_ratings:
            book = Ebook.query.get(book_id)
            book_data = {
                'id': book.id,
                'title': book.title,
                'subtitle': book.subtitle,
                'image': book.image,
                'avg_rating': avg_rating
            }
            bookwith_rating.append(book_data)

        return jsonify({"books": books_data, "basedOnRatings": bookwith_rating})

class Login_(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return jsonify("Could not verify!", 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})
        
        user = User.query.filter_by(email=auth.username).first()
        if not user:
            return jsonify("Could not verify!", 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})
        
        if check_password_hash(password=auth.password, pwhash=user.password):
            is_superuser = False
            if user.role_id == 1:
                is_superuser = True
            token = jwt.encode({'email':user.email, 'is_superuser':is_superuser, 'exp':datetime.datetime.utcnow() + datetime.timedelta(days=1)},secret_key)
            return jsonify({'token': token})
    
        return jsonify("Could not verify!", 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

class CheckAuth(Resource):
    def get(self):
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'isLoggedIn':False}), 401
        
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            return jsonify({'authenticated': True, 'email': data['email'], 'is_superuser': data['is_superuser']})
        except jwt.ExpiredSignatureError:
            return jsonify({'authenticated': False}), 401
        except jwt.InvalidTokenError:
            return jsonify({'authenticated': False}), 401
        
class SearchBooks(Resource):
    def get(self):
        search_pattern = "~"
        keyword = request.args.get('query')
        if keyword:
            keyword = request.args.get('query').strip('"')
            search_pattern = f"%{keyword}%"
        
        author = request.args.get('author', 'none').strip('"')
        genre = request.args.get('genre', 'none').strip('"')
        section = request.args.get('section', 'none').strip('"')

        books = []
        if (search_pattern and author != 'none' and genre != 'none'):
            books = Ebook.query.filter_by(author=author, genre=genre).filter(Ebook.title.like(search_pattern)).all()
        elif (author != 'none' and genre != 'none'):
            books = Ebook.query.filter_by(author=author, genre=genre).all()
        elif (author != 'none' or genre != 'none'):
            books = Ebook.query.filter(or_(Ebook.author==author, Ebook.genre==genre)).all()
        else:
            books = Ebook.query.filter(or_(Ebook.author==author, Ebook.genre==genre, Ebook.sections.any(Section.section_name == section), Ebook.title.like(search_pattern))).all()
        books_dict = marshal(books, book_fields)
        
        return jsonify({
            "book": books_dict,
            })

class SearchTags(Resource):
    def get(self):
        # Distinct name of authors genres sections
        authors_l = Ebook.query.with_entities(Ebook.author).distinct().all()
        genres_l = Ebook.query.with_entities(Ebook.genre).distinct().all()
        sectionss = Section.query.with_entities(Section.section_name).distinct().all()

        authors = [author for (author,) in authors_l]
        genres = [genre for (genre,) in genres_l]
        sections = [section.section_name for section in sectionss]

        return jsonify({"authors": authors,"genres": genres,"sections": sections})
    
class IsBorrowed(Resource):
    @is_user
    def get(current_user, self):
        book_id = request.args.get('book_id')
        is_borrowed = BorrowBook.query.filter_by(book_id=book_id, user_id=current_user.id).first()
        if is_borrowed:
            return jsonify({'isBorrowed': True})
        else:
            return jsonify({'isBorrowed': False})

class Profile(Resource):
    @is_user
    def get(current_user, self):

        user_id = request.args.get('user_id')

        if user_id and current_user.role_id == 1:
            current_user = User.query.filter_by(id=user_id).first()

        pending_requests = db.session.query(RequestBook, Ebook).join(Ebook, RequestBook.book_id == Ebook.id).filter(RequestBook.user_id == current_user.id).all()
        borrowed_books = db.session.query(BorrowBook, Ebook).join(Ebook, BorrowBook.book_id == Ebook.id).filter(BorrowBook.user_id == current_user.id).all()
        returned_books = db.session.query(ReturnBook, Ebook).join(Ebook, ReturnBook.book_id == Ebook.id).filter(ReturnBook.user_id == current_user.id).all()

        p_dict = [{
        "request_id": req.request_id,
        "book_id": req.book_id,
        "user_id": req.user_id,
        "book_details": {
            "title": book.title,
            "subtitle": book.subtitle,
            "image": book.image,
            "author": book.author,
            "pages": book.pages,
            "price": str(book.price),
            "genre": book.genre,
            "file": book.file,
            "created_at": book.created_at.isoformat()
            }
        } for req, book in pending_requests]

        b_dict = [{
        "borrow_id": req.borrow_id,
        "book_id": req.book_id,
        "user_id": req.user_id,
        "release_date": req.release_date,
        "due_date": req.due_date,
        "auto_expiry": req.auto_expiry,
        "book_details": {
            "title": book.title,
            "subtitle": book.subtitle,
            "image": book.image,
            "author": book.author,
            "pages": book.pages,
            "price": str(book.price),
            "genre": book.genre,
            "file": book.file,
            "created_at": book.created_at.isoformat()
            }
        } for req, book in borrowed_books]

        r_dict = [{
        "return_id": req.return_id,
        "book_id": req.book_id,
        "user_id": req.user_id,
        "return_date": req.return_date,
        "book_details": {
            "title": book.title,
            "subtitle": book.subtitle,
            "image": book.image,
            "author": book.author,
            "pages": book.pages,
            "price": str(book.price),
            "genre": book.genre,
            "file": book.file,
            "created_at": book.created_at.isoformat()
            }
        } for req, book in returned_books]

        # Auto expiry after due date
        borrowed_books = BorrowBook.query.filter_by(user_id=current_user.id).all()
        for book in borrowed_books:
            if book.auto_expiry:
                if datetime.datetime.now() > book.due_date:
                    borrow = BorrowBook.query.filter_by(book_id=book.book_id).first()
                    returned_book = ReturnBook(user_id=current_user.id, book_id=book.book_id)
                    db.session.add(returned_book)
                    db.session.delete(borrow)
                    db.session.commit()
    
        return jsonify({'pending_requests': p_dict, 'borrowed_books': b_dict, 'returned_books': r_dict})

class ReqBook(Resource):
    @is_user
    def get(current_user, self):
        book_id = request.args.get("book_id")
        book_exists = Ebook.query.filter_by(id=book_id).first()
        if not(current_user.role_id == 1):
            if_requested = RequestBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
            is_borrowed = BorrowBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
            if book_exists:
                count_requested_books = RequestBook.query.filter_by(user_id=current_user.id).count()
                count_borrowed_books = BorrowBook.query.filter_by(user_id=current_user.id).count()
                total = int(count_requested_books) + int(count_borrowed_books)
                if total < 5:
                    if not(is_borrowed):
                        if if_requested == None:
                            request_ = RequestBook(user_id=current_user.id, book_id=book_id)
                            db.session.add(request_)
                            db.session.commit()
                            return jsonify({'message':'Book requested. Wait for admin to approve it', 'status': 'success'})
                        else:
                            return jsonify({"message": "Book already requested", 'status': 'info'})
                    else:
                        return jsonify({'message': "Book already borrowed", 'status': 'info'})
                else:
                    return jsonify({'message': 'Request limit reached. Return book or cancel request', 'status': 'warning'})
            else:
                return jsonify({'message': 'Book not found!', 'status': 'error'})
        else:
            return jsonify({'message': 'Admin cannot request for book'})

class RetBook(Resource):
    @is_user
    def get(current_user, self):
        book_id = request.args.get("book_id")
        borrow_id = request.args.get("borrow_id")
        user_id = request.args.get("user_id")
        try:
            if user_id and current_user.role_id == 1:
                current_user = User.query.filter_by(id=user_id).first()
            borrow = BorrowBook.query.filter_by(borrow_id=borrow_id).first()
            returned_book = ReturnBook(user_id=current_user.id, book_id=book_id)
            db.session.add(returned_book)
            db.session.delete(borrow)
            db.session.commit()
            return jsonify({'message': 'Book returned'})
        except:
            return jsonify({'message': 'Error occurred during returning book'})

class CancelRequest(Resource):
    @is_user
    def delete(current_user, self):
        request_id = request.args.get("request_id")
        try:
            cancel_request = RequestBook.query.filter_by(request_id=request_id).first()
            db.session.delete(cancel_request)
            db.session.commit()
            return jsonify({'message': 'Book request cancelled'})
        except:
            return jsonify({'message': 'Error occurred during canceling request'})

class Stats(Resource):
    @is_admin
    def get(current_user, self):
            try:
                total_books = Ebook.query.count()
                total_users = User.query.count() - 1
                total_sections = Section.query.count()
                total_requests = RequestBook.query.count()
                current_borrowed = BorrowBook.query.count()
                total_returned = ReturnBook.query.count()
                last_thirty_days = datetime.datetime.now() - timedelta(days=7)
                active_users = db.session.query(User).filter(User.last_activity > last_thirty_days).count() - 1
                data = {"total_books": total_books, "total_users": total_users, "total_sections": total_sections, "total_requests": total_requests,
                "total_returned": total_returned, "current_borrowed": current_borrowed, "active_users": active_users}
                return jsonify({'data': data})
            except:
                return jsonify({'message': 'Error occured when collecting stats'})

class AllUsers(Resource):
    @is_admin
    @cache.cached(key_prefix="users", timeout=60)
    def get(current_user, self):
        try:
            users = User.query.all()
            result= []
            for user in users:
                user_data= {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'date': user.date,
                    'role': user.role.name,
                    'request_count': user.request_records.count(),
                    'borrow_count': user.borrow_records.count(),
                    'return_count': user.return_records.count()
                }
                result.append(user_data)
            return jsonify({'user_data': result})
        except:
            return jsonify({'message': 'Error occurred while fetching user data'})


class BookRequests(Resource):
    @is_admin
    def get(current_user, self):
            try:
                requests = RequestBook.query.all()
                data = []
                for request in requests:
                    req = {
                        'request_id': request.request_id,
                        'user_id': request.user_id,
                        'book_id': request.book_id,
                        'user_name': request.user.name,
                        'book_name': request.ebook.title,
                        'book_image': request.ebook.image
                    }
                    data.append(req)
                return jsonify({'requests': data})
            except:
                return jsonify({'message': 'Error occurred while fetching requests'})

class RemoveUser(Resource):
    @is_admin
    def delete(current_user, self):
        try:
            user_id = request.args.get('user_id')
            user = User.query.filter_by(id=user_id).first_or_404()
            if user.role_id == 1:
                return jsonify({'message': 'Error removing superuser', 'status': 'error'})
            db.session.delete(user)
            db.session.commit()
            cache.delete('users')
            return jsonify({'message': 'user removed', 'status': 'success'})
        except:
            return jsonify({'message': 'Error removing user', 'status': 'error'})

class ApproveRequest(Resource):
    @is_admin
    def get(current_user, self):
        try:
            request_id = request.args.get('request_id')
            requested_book = RequestBook.query.filter_by(request_id=request_id).first()
            borrow = BorrowBook(book_id=requested_book.book_id, user_id=requested_book.user_id, due_date=get_time()+timedelta(days=BOOK_EXPIRY_TIME))
            db.session.add(borrow)
            db.session.delete(requested_book)
            db.session.commit()
            return jsonify({'message': 'Book approved', 'status': 'success'})
        except:
            return jsonify({'message': 'Error approving request', 'status': 'error'})

# Books not in a specific section.
class BooksNotInSection(Resource):
    def get(self):
        try:
            section_id = request.args.get('section_id')
            section = Section.query.filter_by(section_id=section_id).first()
            books = Ebook.query.filter(not_(Ebook.sections.contains(section))).all()
            books_dict = marshal(books, book_fields)
            return jsonify({'books': books_dict})
        except:
            return jsonify({'message': 'Error fetching book not in section', 'status': 'error'})

class AddBookToSection(Resource):
    @is_admin
    def get(current_user, self):
        try:
            book_id = request.args.get('book_id')
            section_id = request.args.get('section_id')
            ebook = Ebook.query.filter_by(id=book_id).first()
            section = Section.query.filter_by(section_id=section_id).first()
            if ebook in section.ebook:
                return jsonify({'message': 'Book already in section', 'status': 'warning'})
            else:
                ebook.sections.append(section)
                db.session.commit()
                cache.delete('sections')
                return jsonify({'message': 'Book added to section', 'status': 'success'})
        except:
            return jsonify({'message': 'Error adding book to section', 'status': 'error'})

class RemoveBookFromSection(Resource):
    @is_admin
    def delete(current_user, self):
        try:
            book_id = request.args.get('book_id')
            section_id = request.args.get('section_id')
            ebook = Ebook.query.filter_by(id=book_id).first()
            section = Section.query.filter_by(section_id=section_id).first()
            if ebook in section.ebook:
                ebook.sections.remove(section)
                db.session.commit()
                cache.delete('sections')
                return jsonify({'message': 'Book removed', 'status': 'success'})
            else:
                return jsonify({'message': 'Book not in section', 'status': 'error'})
        except:
            return jsonify({'message': 'Error removing book from section', 'status': 'error'})
        
class CreateAccount(Resource):
    def post(self):
        data = request.get_json()

        try:
            email_exsist = db.session.query(User).filter_by(email=data.get('email')).first()

            if email_exsist:
                return jsonify({"message": "You're already singned up with this email.", "status": "info"})
            else:
                hashed_pass = generate_password_hash(salt_length=8, password=data.get('password'))

                new_user = User(name=data.get('name'), email=data.get('email'), password=hashed_pass, role_id=2)
                db.session.add(new_user)
                db.session.commit()
                cache.delete('users')

                token = jwt.encode({'email':new_user.email, 'is_superuser':False, 'exp':datetime.datetime.utcnow() + datetime.timedelta(days=1)},secret_key)
                return jsonify({'token': token})
        except:
            return jsonify({'message': 'Error while creating account', 'status': 'error'})

class ToggleExpiry(Resource):
    @is_user
    def post(current_user, self):
        try:
            data = request.get_json()
            borrow_id = data.get('borrow_id')
            borrow_book = BorrowBook.query.filter_by(borrow_id=borrow_id).first()
            if borrow_book.auto_expiry:
                borrow_book.auto_expiry = False
                db.session.commit()
                return jsonify({'message': 'Auto expiry set to manual', 'status': 'success'})
            else:
                borrow_book.auto_expiry = True
                borrow_book.due_date = get_time()+timedelta(days=BOOK_EXPIRY_TIME)
                db.session.commit()
                return jsonify({'message': 'Auto expire after 7 days', 'status': 'success'})
        except:
            return jsonify({'message': 'Error updating expiry period', 'status': 'error'})


class RequestData(Resource):
    @is_user
    def post(current_user, self):
        from tasks import generate_csv
        try:
            task = generate_csv.delay(current_user.id)
            return jsonify({'task_id': task.id, 'message': 'Data requested wait some time', 'status': 'info'})
        except:
            return jsonify({'message': 'Error requesting data', 'status': 'error'})

class DownloadData(Resource):
    @is_user
    def get(current_user, self):
        from tasks import generate_csv
        try:
            task_id = request.args.get('task_id')
            task = AsyncResult(task_id, app=generate_csv)
            if task.state == 'SUCCESS':
                csv_file_path = task.result.split('static')[1]
                return jsonify({'path': csv_file_path, 'message': 'Data export complete', 'status': 'success'})
            elif task.state == 'FAILURE':
                return jsonify({'message': f'Failed {task.info}', 'status': 'error'})
            else:
                return jsonify({'message': 'Still processing. please wait', 'status': 'info'})
        except:
            return jsonify({'message': 'Error downloading data', 'status': 'error'})

class RateBook(Resource):
    @is_user
    def post(current_user, self):
        book_id = request.form.get('book_id')
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        try:
            rating = Rating(comment=comment, rating=rating, book_id=book_id, user_id=current_user.id)
            db.session.add(rating)
            db.session.commit()
            cache.delete('books')
            return jsonify({'message': 'Rating posted', 'status': 'success'})
        except:
            return jsonify({'message': 'Error rating book', 'status': 'error'})

class DeleteRating(Resource):
    @is_admin
    def delete(current_user, self):
        comment_id = request.args.get('comment_id')
        try:
            comment = Rating.query.filter_by(id=comment_id).first_or_404()
            db.session.delete(comment)
            db.session.commit()
            cache.delete('books')
            return jsonify({'message': 'Rating deleted', 'status': 'success'})
        except:
            return jsonify({'message': 'Error deleting rating', 'status': 'error'})
        
class Ratings(Resource):
    def get(self):
        book_id = request.args.get('book_id')
        try:
            book = Ebook.query.filter_by(id=book_id).first_or_404()
            ratings = book.ratings
            data = []
            for rating in ratings:
                r = {
                    'id': rating.id,
                    'rating': rating.rating,
                    'comment': rating.comment,
                    'user_id': rating.user_id,
                    'created_at': rating.created_at,
                    'user_name': rating.user.name
                }
                data.append(r)
            return jsonify({'ratings': data})
        except:
            return jsonify({'message': "Error fetching ratings", 'status': 'error'}), 404

class GrantBook(Resource):
    @is_admin
    def post(current_user, self):
        data = request.get_json()
        book_id = data.get('book_id')
        user_id = data.get('user_id')
        try:
            user = User.query.filter_by(id=user_id).first_or_404()
            book = Ebook.query.filter_by(id=book_id).first_or_404()
            borrow = BorrowBook.query.filter_by(user_id=user.id , book_id=book.id).first()
            if borrow:
                return jsonify({'message': 'Book already borrowed', 'status': 'info'})
            else:
                borrow = BorrowBook(book_id=book.id, user_id=user.id, due_date=get_time()+timedelta(days=BOOK_EXPIRY_TIME))
                db.session.add(borrow)
                r_book = RequestBook.query.filter_by(user_id=user.id, book_id=book.id).first()
                if r_book:
                    db.session.delete(r_book)
                db.session.commit()
                return jsonify({'message': 'Book granted', 'status': 'success'})
        except:
            return jsonify({'message': 'Error while granting book', 'status': 'error'})

class BookPurchase(Resource):
    @is_user
    def post(current_user, self):
        data = request.get_json()
        book_id = data.get('book_id')
        amount = data.get('amount')
        is_purchased = Purchase.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if is_purchased:
            return jsonify({'message': 'Book already purchased', 'status': 'warning'})
        try:
            book = Ebook.query.filter_by(id=book_id).first_or_404()
            payment = Purchase(book_id=book.id, amount=amount, user_id=current_user.id)
            db.session.add(payment)
            db.session.commit()
            return jsonify({'message': 'Book successfully purchased', 'status': 'success'})
        except:
            return jsonify({'message': 'Error while purchasing book', 'status': 'error'})

class IsPurchased(Resource):
    @is_user
    def get(current_user, self):
        book_id = request.args.get('book_id')
        print(book_id)
        user_id = current_user.id
        try:
            is_purchased = Purchase.query.filter_by(book_id=book_id, user_id=user_id).first()
            if is_purchased:
                return jsonify({'is_purchased': True})
            return jsonify({'is_purchased': False})
        except:
            return jsonify({'message': 'Error fetching purchase data', 'status': 'error'})
        