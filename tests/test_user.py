import pytest
from sqlalchemy.exc import IntegrityError
from app.auth.utils import get_password_hash, verify_password
from app.auth.models import User

# Sample data for testing
USERNAME = "testuser"
PASSWORD = "testpassword"
EMAIL = "testuser@example.com"

# Test creating a user and verifying data integrity
def test_create_user(fakedb):
    hashed_password = get_password_hash(PASSWORD)
    user = User(username=USERNAME, email=EMAIL, hashed_password=hashed_password)

    fakedb.add(user)
    fakedb.commit()
    fakedb.refresh(user)

    assert user.username == USERNAME
    assert user.email == EMAIL
    assert user.hashed_password != PASSWORD  # Ensure password is hashed

# Test unique constraint on email
def test_unique_email_constraint(fakedb):
    hashed_password = get_password_hash("testpassword")
    user1 = User(username="uniqueuser1", email="unique@example.com", hashed_password=hashed_password)
    user2 = User(username="uniqueuser2", email="unique@example.com", hashed_password=hashed_password)

    fakedb.add(user1)
    fakedb.commit()

    fakedb.add(user2)
    with pytest.raises(IntegrityError):
        fakedb.commit()

    fakedb.rollback()

def test_password_hashing():
    hashed_password = get_password_hash(PASSWORD)
    assert hashed_password != PASSWORD
    assert verify_password(PASSWORD, hashed_password)

def test_verify_password():
    hashed_password = get_password_hash(PASSWORD)
    assert verify_password(PASSWORD, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)
