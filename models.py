from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

def get_time():
    current_time = datetime.now()
    return current_time.replace(microsecond=0)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=get_time)
    active = db.Column(db.Boolean(), default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), unique=False, nullable=False)
    last_activity = db.Column(db.DateTime(timezone=True), nullable=True)
    
    role = db.relationship('Role', back_populates='user', uselist=False)
    ebooks = relationship('Ebook', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    request_records = relationship('RequestBook', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    borrow_records = relationship('BorrowBook', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    return_records = relationship('ReturnBook', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    purchase_records = relationship('Purchase', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    ratings = relationship('Rating', backref='user')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', back_populates='role', uselist=False)


class Ebook(db.Model):
    __tablename__ = 'ebook'
    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # owner = relationship("User", back_populates="ebooks")
    author = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255), nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    file = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)

    sections = db.relationship('Section', secondary='book_section', backref='ebook')
    requests_ = db.relationship('RequestBook', backref='ebook', cascade='all, delete-orphan')
    borrows_ = db.relationship('BorrowBook', backref='ebook', cascade='all, delete-orphan')
    returns_ = db.relationship('ReturnBook', backref='ebook', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='ebook', cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime(timezone=True), default=get_time)
    # updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now().replace(microsecond=0))

    def average_rating(self):
        return db.session.query(func.avg(Rating.rating)).filter(Rating.book_id == self.id).scalar()

    def to_json(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "subtitle": self.subtitle,
            "pages": self.pages,
            "price": self.price,
            "genre": self.genre,
            "file": self.file,
            "image": self.image,
            "created_at": self.created_at

        }
    
    def __repr__(self):
        return f"{self.id}"

class RequestBook(db.Model):
    __tablename__ = 'request_record'
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('ebook.id'))

class BorrowBook(db.Model):
    __tablename__ = 'borrow_record'
    borrow_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('ebook.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    release_date = db.Column(db.DateTime(timezone=True), default=get_time)
    due_date = db.Column(db.DateTime(timezone=True), default=get_time)
    auto_expiry = db.Column(db.Boolean(), default=True)

class ReturnBook(db.Model):
    __tablename__ = 'return_record'
    return_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('ebook.id'))
    return_date = db.Column(db.DateTime(timezone=True), default=get_time)

book_section = db.Table('book_section', 
                        db.Column('ebook_id', db.Integer, db.ForeignKey('ebook.id')),
                        db.Column('section_id', db.Integer, db.ForeignKey('section.section_id')),
                        )

class Section(db.Model):
    __tablename__= 'section'
    section_id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_time)

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, default=0)
    comment = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('ebook.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_time)

class Purchase(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('ebook.id'), nullable=False)
    purchase_date = db.Column(db.DateTime(timezone=True), default=get_time)
    amount = db.Column(db.Float, nullable=False)
