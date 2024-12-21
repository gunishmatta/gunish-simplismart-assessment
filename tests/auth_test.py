from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.core.security import get_password_hash

from app.models.user import User as UserModel



def create_user(db: Session, username: str, email: str, password: str) -> UserModel:
	hashed_password = get_password_hash(password)
	user = UserModel(username=username, email=email, hashed_password=hashed_password, is_active=True)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def test_register(client: TestClient, db: Session):
	# Register a new user
	response = client.post("/auth/register", json={
		"username": "testuser",
		"email": "testuser@example.com",
		"password": "password123"
	})

	assert response.status_code == 200
	data = response.json()
	assert "id" in data
	assert data["username"] == "testuser"
	assert data["email"] == "testuser@example.com"


def test_register_existing_user(client: TestClient, db: Session):
	# First create a user
	create_user(db, "testuser", "testuser@example.com", "password123")

	# Try to register with the same username
	response = client.post("/register", json={
		"username": "testuser",
		"email": "testuser@example.com",
		"password": "password123"
	})

	assert response.status_code == 400
	assert response.json() == {"detail": "Username or email already exists"}


def test_login(client: TestClient, db: Session):
	# First create a user
	create_user(db, "testuser", "testuser@example.com", "password123")

	# Login with correct credentials
	response = client.post("/login", data={
		"username": "testuser",
		"password": "password123"
	})

	assert response.status_code == 200
	assert response.json() == {"message": "Login successful"}

	# Check if session cookie is set
	cookies = response.cookies
	assert "user_id" in cookies


def test_login_invalid_credentials(client: TestClient, db: Session):
	# First create a user
	create_user(db, "testuser", "testuser@example.com", "password123")

	# Attempt login with incorrect password
	response = client.post("/login", data={
		"username": "testuser",
		"password": "wrongpassword"
	})

	assert response.status_code == 401
	assert response.json() == {"detail": "Invalid username or password"}


def test_logout(client: TestClient, db: Session):
	# First create a user and login
	create_user(db, "testuser", "testuser@example.com", "password123")
	response = client.post("/login", data={
		"username": "testuser",
		"password": "password123"
	})

	cookies = response.cookies
	assert "user_id" in cookies

	# Logout
	response = client.post("/logout", cookies=cookies)
	assert response.status_code == 200
	assert response.json() == {"message": "Successfully logged out"}

	# After logout, check that user_id cookie is cleared
	response = client.post("/logout", cookies=cookies)
	assert response.status_code == 200
	assert response.json() == {"message": "Successfully logged out"}
	assert "user_id" not in response.cookies
