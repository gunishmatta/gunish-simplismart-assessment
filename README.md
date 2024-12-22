# Hypervisor-like Service for MLOps Platform

## Overview
This is a FastAPI-based technical assessment designed to evaluate backend system design and implementation skills. The project implements a cluster management system with session-based authentication, organization management, and deployment scheduling.

## Assessment Tasks

### 1. User Authentication and Organization Management
- [ ] Implement session-based user authentication (login/logout)
- [ ] Complete user registration with password hashing
- [ ] Add organization creation with random invite codes
- [ ] Implement organization joining via invite codes

### 2. Cluster Management
- [ ] Create clusters with resource limits (CPU, RAM, GPU)
- [ ] Implement resource tracking and availability
- [ ] Add cluster listing for organization members
- [ ] Validate resource constraints

### 3. Deployment Management
- [ ] Develop a preemption-based scheduling algorithm to prioritize high-priority deployments
- [ ] Create deployment endpoints with resource requirements
- [ ] Implement basic scheduling algorithm
- [ ] Add deployment status tracking
- [ ] Handle resource allocation/deallocation

### 4. Advanced Features (Optional)
- [ ] Add support for deployment dependency management (e.g., Deployment A must complete before Deployment B starts)
- [ ] Implement Role-Based Access Control (RBAC)
- [ ] Add rate limiting
- [ ] Create comprehensive test coverage
- [ ] Enhance API documentation

## Project Structure
```
.
├── app
│   ├── api
│   │   └── v1
│   │       ├── endpoints
│   │       │   ├── auth.py        # Authentication endpoints
│   │       │   ├── clusters.py    # Cluster management
│   │       │   ├── deployments.py # Deployment handling
│   │       │   └── organizations.py # Organization management
│   │       └── api.py
│   ├── core
│   │   ├── config.py   # Configuration settings
│   │   ├── deps.py     # Dependencies and utilities
│   │   └── security.py # Security functions
│   ├── db
│   │   ├── base.py    # Database setup
│   │   └── session.py # Database session
│   ├── models         # SQLAlchemy models
│   │   ├── cluster.py
│   │   ├── deployment.py
│   │   ├── organization.py
│   │   └── user.py
│   ├── schemas       # Pydantic schemas
│   │   ├── cluster.py
│   │   ├── deployment.py
│   │   ├── organization.py
│   │   └── user.py
│   └── main.py      # Application entry point
└── tests
    ├── conftest.py  # Test configuration
    └── test_api     # API tests
```

## Authentication Flow
1. Register a new user (`POST /api/v1/auth/register`)
2. Login with credentials (`POST /api/v1/auth/login`)
   - Server sets a secure session cookie
3. Use session cookie for authenticated requests
4. Logout when finished (`POST /api/v1/auth/logout`)

## Organization Management
1. Create organization (generates invite code)
2. Share invite code with team members
3. Members join using invite code
4. Access organization resources (clusters, deployments)

## Testing
Run the test suite:
```bash
pytest
```

## Evaluation Criteria

### 1. Code Quality (40%)
- Clean, readable, and well-organized code
- Proper error handling
- Effective use of FastAPI features
- Type hints and validation

### 2. System Design (30%)
- Authentication implementation
- Resource management approach
- Scheduling algorithm design
- API structure

### 3. Functionality (20%)
- Working authentication system
- Proper resource tracking
- Successful deployment scheduling
- Error handling

### 4. Testing & Documentation (10%)
- Test coverage
- API documentation
- Code comments
- README completeness

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database

### Setup Instructions
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Session Configuration
SECRET_KEY=your-secret-key  # For secure session encryption
SESSION_COOKIE_NAME=session  # Cookie name for the session
SESSION_MAX_AGE=1800        # Session duration in seconds (30 minutes)
```

3. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes
- Focus on implementing core features first
- Use appropriate error handling throughout
- Document your design decisions
- Consider edge cases in your implementation

**App Design**

The design of the application is structured around modular components that facilitate easy scalability and testing. The main components include:

1. Services Layer (deployment_service.py)
The core logic for handling deployments is implemented here. This layer is responsible for:
Creating, updating, and scheduling deployments.
Managing deployment preemption based on different strategies (e.g., Priority Preemption).
Applying resource changes to clusters based on deployment requests.
2. Models Layer (models)
Represents the structure of the data in the database, such as clusters and deployments.
Models interact with the database via SQLAlchemy ORM.
Example models include Cluster, Deployment, and User.
3. Schemas Layer (schemas)
Defines the Pydantic models used for request validation and response formatting.
Includes models like DeploymentCreate, DeploymentUpdate, and Deployment.
4. API Layer (main.py)
This is where the FastAPI application is defined, including the routing for different endpoints (e.g., for deployment creation, cluster status checking).
The application uses dependency injection to manage database sessions and user authentication.
5. Preemption Strategies (preemption_strategy.py)
Defines different strategies for preempting existing deployments to make room for new ones, based on user-defined priorities or other criteria.
Testing Design
The app follows a test-driven development approach, with all core functionalities being tested. Unit tests are used to verify the behavior of individual components, while integration tests ensure that the system works as expected end-to-end.

Tests are written using the pytest framework and are structured into the following categories:

Unit Tests: For testing individual service methods and preemption strategies.
API endpoints are covered using TestClient from FastAPI.

**Instructions to Run the App with Docker**

To run this app inside a Docker container, follow the steps below.

Prerequisites
* Docker installed on your machine.
* Docker Compose


**Clone the Repository**
Clone the repository to your local machine:
`git clone <repo_url>`
`cd your-repository-directory`

To run the application using Docker Compose, use the following command:
`docker-compose up --build`

**Verify the Application is Running**
Once the application is running, open your browser or use a tool like curl or Postman to interact with the API:

`curl http://localhost:8000/docs`