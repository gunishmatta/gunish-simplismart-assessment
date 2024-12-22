import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.cluster import Cluster
from app.models.deployment import Deployment, DeploymentStatus
from tests.test_cluster import create_cluster
from tests.test_organization import create_organization, create_user, login_user


@pytest.fixture
def setup_test_data(db: Session):
    """
    Fixture to create initial test data
    """
    def _setup_test_data():
        organization = create_organization(db, name="Test Organization", invite_code="INVITE123")
        user = create_user(db, username="testuser", email="testuser@example.com", password="password123")
        user.organization_id = organization.id
        db.commit()

        cluster = create_cluster(db, name="Test Cluster", organization_id=organization.id, cpu_limit=30, ram_limit=40, gpu_limit=40)
        return organization, user, cluster
    return _setup_test_data

def test_create_deployment(client: TestClient, db: Session, setup_test_data):
    """
    Test for creating a deployment
    """
    organization, user, cluster = setup_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    payload = {
        "name": "Test Deployment",
        "cpu_required": 8,
        "ram_required": 16,
        "gpu_required": 2,
        "priority": 1,
	    "docker_image":"abc",
        "cluster_id": cluster.id
    }

    response = client.post("/api/v1/deployments/", json=payload, cookies=cookies)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["cpu_required"] == payload["cpu_required"]
    assert data["ram_required"] == payload["ram_required"]
    assert data["gpu_required"] == payload["gpu_required"]
    assert data["status"] == DeploymentStatus.PENDING.value

    deployment = db.query(Deployment).filter_by(name="Test Deployment").first()
    assert deployment is not None
    assert deployment.cluster_id == cluster.id

def test_create_deployment_with_insufficient_resources(client: TestClient, db: Session, setup_test_data):
    """
    Test for deployment creation when resources are insufficient
    """
    _, user, cluster = setup_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    payload = {
        "name": "Deployment Insufficient",
        "cpu_required": 60,  # Exceeds available CPU
        "ram_required": 32,
        "gpu_required": 4,
        "priority": 1,
        "docker_image": "abc",
        "cluster_id": cluster.id
    }

    response = client.post("/api/v1/deployments/", json=payload, cookies=cookies)
    assert response.status_code == 400

def test_list_deployments(client: TestClient, db: Session, setup_test_data):
    """
    Test for listing deployments
    """
    _, user, cluster = setup_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    deployment1 = Deployment(name="Deployment A", cpu_required=4, ram_required=8, gpu_required=1, cluster_id=cluster.id, docker_image='abc', priority=1, status=DeploymentStatus.RUNNING.name)
    deployment2 = Deployment(name="Deployment B", cpu_required=4, ram_required=8, gpu_required=1, cluster_id=cluster.id,docker_image='abc', priority=2, status=DeploymentStatus.PENDING.name)
    db.add_all([deployment1, deployment2])
    db.commit()

    response = client.get("/api/v1/deployments/", cookies=cookies)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    deployment_names = [deployment["name"] for deployment in data]
    assert "Deployment A" in deployment_names
    assert "Deployment B" in deployment_names

def test_list_deployments_no_clusters(client: TestClient, db: Session, setup_test_data):
    """
    Test for listing deployments when no clusters exist for the user's organization
    """
    _, user, _ = setup_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    # Delete the cluster
    db.query(Cluster).delete()
    db.commit()

    response = client.get("/api/v1/deployments/", cookies=cookies)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No clusters found for the user's organization."

def test_list_deployments_no_deployments(client: TestClient, db: Session, setup_test_data):
    """
    Test for listing deployments when no deployments exist
    """
    _, user, cluster = setup_test_data()
    cookies = login_user(client, username="testuser", password="password123")

    response = client.get("/api/v1/deployments/", cookies=cookies)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No deployments found for the user's organization."
