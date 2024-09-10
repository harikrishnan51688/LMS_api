from models import db
from models import User, Role
from werkzeug.security import generate_password_hash


def setup_db():
    
    if not Role.query.first():
        admin_role = Role(name='librarian', description='library admin')
        user_role = Role(name='user', description='general user')
        db.session.add_all([admin_role, user_role])
        db.session.commit()

    if not User.query.first():
        hashed_pass = generate_password_hash(salt_length=8, password='12345678')
        admin_user = User(name='admin', email='admin@email.com', password=hashed_pass, role_id=1)
        db.session.add_all([admin_user])
        db.session.commit()
        print('Database initial setup complete')
