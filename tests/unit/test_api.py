def test_root_returns_welcome_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from fastapi-blog!"}


def test_api_routes_are_versioned(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert set(response.json()["paths"]) == {
        "/api/v1/posts",
        "/api/v1/posts/{post_id}",
        "/api/v1/users/register",
    }



def test_get_posts_returns_database_posts(client):
    response = client.get("/api/v1/posts")

    assert response.status_code == 200
    assert response.json()["data"] == [
        {
            "id": 1,
            "title": "Database Post",
            "content": "Loaded from PostgreSQL",
            "published": True,
            "rating": 5,
            "created_at": "2026-10-24T00:00:00Z",
            "updated_at": "2026-10-24T00:00:00Z",
        }
    ]
    assert response.json()["pagination"] == {
        "total": 1,
        "page": 1,
        "limit": 10,
        "total_pages": 1,
    }


def test_get_posts_supports_pagination_query_parameters(client):
    response = client.get("/api/v1/posts?page=2&limit=5")

    assert response.status_code == 200
    assert response.json()["pagination"] == {
        "total": 1,
        "page": 2,
        "limit": 5,
        "total_pages": 1,
    }



def test_get_posts_rejects_invalid_pagination_parameters(client):
    response = client.get("/api/v1/posts?page=0&limit=200")

    assert response.status_code == 422



def test_create_post_persists_post(client, db_session):
    response = client.post(
        "/api/v1/posts",
        json={"title": "Created", "content": "From API", "published": True, "rating": 4},
    )

    assert response.status_code == 201
    assert response.json()["data"]["id"] == 1
    assert response.json()["data"]["created_at"] == "2026-10-24T00:00:00Z"
    assert response.json()["data"]["updated_at"] == "2026-10-24T00:00:00Z"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()


def test_get_post_returns_database_post(client):
    response = client.get("/api/v1/posts/1")

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Database Post"


def test_update_post_persists_changes(client, db_session):
    response = client.put(
        "/api/v1/posts/1",
        json={"title": "Updated", "content": "Updated content", "published": False},
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated"
    db_session.commit.assert_called_once()


def test_delete_post_persists_deletion(client, db_session):
    response = client.delete("/api/v1/posts/1")

    assert response.status_code == 204
    db_session.delete.assert_called_once()
    db_session.commit.assert_called_once()


def test_missing_post_returns_404(client, db_session):
    db_session.get.return_value = None

    response = client.get("/api/v1/posts/99")

    assert response.status_code == 404


def test_user_registration_persists_user_with_hashed_password(client, db_session):
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "johndoe",
            "email": "john@example.com",
            "password": "supersecretpassword",
        },
    )

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["message"] == "User registered successfully"
    assert json_data["data"]["id"] == 1
    assert json_data["data"]["username"] == "johndoe"
    assert json_data["data"]["email"] == "john@example.com"
    # Ensure plain password is never exposed in the response
    assert "password" not in json_data["data"]

    # Verify database persistence and password hashing
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    added_user = db_session.add.call_args[0][0]
    assert added_user.username == "johndoe"
    assert added_user.email == "john@example.com"
    assert added_user.password != "supersecretpassword"
    # Verify hashed password using security verification
    from app.core.security import verify_password

    assert verify_password("supersecretpassword", added_user.password)


def test_user_registration_duplicate_email_fails(client, db_session):
    db_session.scalar.side_effect = None
    from unittest.mock import MagicMock

    db_session.scalar.return_value = MagicMock(id=1, email="john@example.com")

    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "john@example.com",
            "password": "supersecretpassword",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"


def test_user_registration_duplicate_username_fails(client, db_session):
    from unittest.mock import MagicMock

    def mock_scalar_username(statement=None, *args, **kwargs):
        if (
            statement is not None
            and hasattr(statement, "whereclause")
            and statement.whereclause is not None
        ):
            where_str = str(statement.whereclause).lower()
            if "username" in where_str:
                return MagicMock(id=1, username="johndoe")
        return None

    db_session.scalar.side_effect = mock_scalar_username

    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "johndoe",
            "email": "other@example.com",
            "password": "supersecretpassword",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username is already taken"


def test_user_registration_invalid_input_validation(client):
    # Invalid email format
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "johndoe",
            "email": "not-an-email",
            "password": "validpassword",
        },
    )
    assert response.status_code == 422

    # Short password (< 6 chars)
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "johndoe",
            "email": "john@example.com",
            "password": "123",
        },
    )
    assert response.status_code == 422

