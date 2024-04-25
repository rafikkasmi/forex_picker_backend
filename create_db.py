# create_db.py
from main import db
from main import app
from models.models import User

# Create tables
with app.app_context():
    db.create_all()

# Add a user
new_user = User(username='john_doe', email='john@example.com')
db.session.add(new_user)
db.session.commit()

# Query all users
all_users = User.query.all()
print(all_users)