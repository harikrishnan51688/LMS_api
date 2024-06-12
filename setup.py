from main import app
from models import db
from models import User, Role
from api import cache
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

db.init_app(app)
cache.init_app(app)
migrate = Migrate(app, db)

def setup_db():
    with app.app_context():
        # db.drop_all()
        db.create_all()

        if not Role.query.first():
            admin_role = Role(name='admin', description='superuser')
            user_role = Role(name='user', description='general user')
            db.session.add_all([admin_role, user_role])
            db.session.commit()

        if not User.query.first():
            hashed_pass = generate_password_hash(salt_length=8, password='12345678')
            admin_user = User(name='admin', email='admin@email.com', password=hashed_pass, role_id=1)
            db.session.add_all([admin_user])
            db.session.commit()
            print('Database initial setup complete')