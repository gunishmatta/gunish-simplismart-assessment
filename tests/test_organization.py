from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.core.security import get_password_hash
from app.models.organization import Organization as OrganizationModel
from app.models.user import User as UserModel
from app.schemas.organizationresponse import OrganizationCreate


def create_user(db: Session, username: str, email: str, password: str) -> UserModel:
	hashed_password = get_password_hash(password)
	user = UserModel(username=username, email=email, hashed_password=hashed_password, is_active=True)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def create_organization(db: Session, name: str, invite_code: str) -> OrganizationModel:
	organization = OrganizationModel(name=name, invite_code=invite_code)
	db.add(organization)
	db.commit()
	db.refresh(organization)
	return organization


def login_user(client: TestClient, username: str, password: str) -> dict:
	response = client.post("/api/v1/auth/login", json={
		"username": username,
		"password": password
	})
	cookies = response.cookies
	return cookies


def test_create_organization(client: TestClient, db: Session):
	create_user(db, "testuser", "testuser@example.com", "password123")
	cookies = login_user(client, "testuser", "password123")

	# Create the organization
	response = client.post("/api/v1/organizations/", json={
		"name": "Test Organization"
	}, cookies=cookies)

	assert response.status_code == 200
	data = response.json()
	assert "id" in data
	assert data["name"] == "Test Organization"


# Test for attempting to create an organization with an existing name
def test_create_organization_existing_name(client: TestClient, db: Session):
	create_user(db, "testuser", "testuser@example.com", "password123")
	cookies = login_user(client, "testuser", "password123")

	create_organization(db, "Existing Organization", "invite123")

	response = client.post("/api/v1/organizations/", json={
		"name": "Existing Organization"
	}, cookies=cookies)

	assert response.status_code == 400
	assert response.json() == {"detail": "Organization with this name already exists."}


def test_join_organization(client: TestClient, db: Session):
	user = create_user(db, "testuser", "testuser@example.com", "password123")
	cookies = login_user(client, "testuser", "password123")
	organization = create_organization(db, "Test Organization", "invite123")

	response = client.post(f"/api/v1/organizations/{organization.invite_code}/join", json={}, cookies=cookies)

	assert response.status_code == 200
	assert user.organization_id == organization.id


def test_join_organization_invalid_invite_code(client: TestClient, db: Session):
	create_user(db, "testuser", "testuser@example.com", "password123")
	cookies = login_user(client, "testuser", "password123")

	response = client.post("/api/v1/organizations/invalidinvitecode/join", json={}, cookies=cookies)

	assert response.status_code == 404
	assert response.json() == {"detail": "Organization not found"}


def test_join_organization_already_member(client: TestClient, db: Session):
	user = create_user(db, "testuser", "testuser@example.com", "password123")
	cookies = login_user(client, "testuser", "password123")
	organization = create_organization(db, "Test Organization", "invite123")

	client.post(f"/api/v1/organizations/{organization.invite_code}/join", json={}, cookies=cookies)

	response = client.post(f"/api/v1/organizations/{organization.invite_code}/join", json={}, cookies=cookies)

	assert response.status_code == 400
	assert response.json() == {"detail": "User is already a member of an organization"}
