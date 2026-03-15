from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """
    Test the user registration endpoint.
    """
    print("Testing: User registration process...")
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ai_engineer@hcmc.com",
            "password": "securepassword2357",
            "full_name": "Nguyen Van Duc",
        },
    )

    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    print("Success: User registered and token received.")


def test_register_existing_user(client: TestClient):
    """
    Test that registering an already existing email returns a 400 error.
    """
    print("Testing: Duplicate user registration blocking...")
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ai_engineer@hcmc.com",
            "password": "anotherpassword",
            "full_name": "Nguyen Van Duc Clone",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
    print("Success: Duplicate email blocked correctly.")


def test_login_user(client: TestClient):
    """
    Test the user login endpoint using OAuth2 form data.
    """
    print("Testing: User login process...")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "ai_engineer@hcmc.com", "password": "securepassword2357"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    print("Success: User logged in successfully.")
