import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.cluster import Cluster
from tests.test_organization import create_organization, create_user, login_user


@pytest.fixture
def create_test_data(db: Session):
    """
    Fixture to create initial test data
    """
    def _create_test_data():
        organization = create_organization(db, name="Test Organization", invite_code="INVITE123")
        user = create_user(db, username="testuser", email="testuser@example.com", password="password123")
        user.organization_id = organization.id
        db.commit()
        return organization, user
    return _create_test_data

def create_cluster(db: Session, name: str, organization_id: int, cpu_limit: int, ram_limit: int, gpu_limit: int) -> Cluster:
    """
    Utility function to create a cluster
    """
    cluster = Cluster(
        name=name,
        organization_id=organization_id,
        cpu_limit=cpu_limit,
        ram_limit=ram_limit,
        gpu_limit=gpu_limit,
        cpu_available=cpu_limit,
        ram_available=ram_limit,
        gpu_available=gpu_limit
    )
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    return cluster

def test_create_cluster(client: TestClient, db: Session, create_test_data):
    """
    Test for creating a cluster
    """
    # Setup initial data
    organization, user = create_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    payload = {
        "name": "Test Cluster",
        "cpu_limit": 16,
        "ram_limit": 32,
        "gpu_limit": 4,
        "organization_id": organization.id
    }

    response = client.post("/api/v1/clusters/", json=payload, cookies=cookies)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["cpu_limit"] == payload["cpu_limit"]
    assert data["ram_limit"] == payload["ram_limit"]
    assert data["gpu_limit"] == payload["gpu_limit"]

    cluster = db.query(Cluster).filter_by(name="Test Cluster").first()
    assert cluster is not None
    assert cluster.organization_id == organization.id

def test_list_clusters(client: TestClient, db: Session, create_test_data):
    """
    Test for listing clusters
    """
    organization, user = create_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    create_cluster(db, name="Cluster A", organization_id=organization.id, cpu_limit=16, ram_limit=32, gpu_limit=4)
    create_cluster(db, name="Cluster B", organization_id=organization.id, cpu_limit=8, ram_limit=16, gpu_limit=2)

    response = client.get("/api/v1/clusters/", cookies=cookies)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    cluster_names = [cluster["name"] for cluster in data]
    assert "Cluster A" in cluster_names
    assert "Cluster B" in cluster_names


def test_list_clusters_without_organization(client: TestClient, db: Session):
    """
    Test for listing clusters without belonging to an organization
    """
    user = create_user(db, username="user_no_org", email="user_no_org@example.com", password="password123")
    cookies = login_user(client, username="user_no_org", password="password123")

    response = client.get("/api/v1/clusters/", cookies=cookies)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User must belong to an organization to view clusters."
