from app.auth.utils import get_password_hash
from app.auth.models import User
from sqlalchemy.orm import Session

from app.items.models import Item


def create_test_user(db: Session, username="testuser", email="testuser@example.com", password="password"):
    """Helper function to create a user for testing."""
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Helper function to create an item for a user
def create_test_item(db, user_id, name="Test Item", description="Test Description", price=100.0):
    item = Item(name=name, description=description, price=price, user_id=user_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Helper function to create multiple test items
def create_test_items(db, user_id):
    items = [
        {"name": "test Item 1", "description": "Description 1", "price": 10.0},
        {"name": "test Item 2", "description": "Description 2", "price": 20.0},
        {"name": "very very expensive Item", "description": "ouch", "price": 1000.0},
    ]
    for item_data in items:
        item = Item(user_id=user_id, **item_data)
        db.add(item)
    db.commit()
