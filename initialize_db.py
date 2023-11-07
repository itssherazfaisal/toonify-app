from app import db, User
from werkzeug.security import generate_password_hash
import uuid
# Create the database and tables
db.create_all()

# Check if the dummy user already exists
dummy_user = User.query.filter_by(email='test@gmail.com').first()

if not dummy_user:
    # Create a new User object with the dummy user's data
    dummy_user = User(
        public_id=str(uuid.uuid4()),  # Generate a unique public_id
        name='demo',
        email='test@gmail.com',
        password=generate_password_hash('test123')
    )

    # Add the dummy user to the database
    db.session.add(dummy_user)
    db.session.commit()

    print('Dummy user added successfully.')
else:
    print('Dummy user already exists in the database.')
