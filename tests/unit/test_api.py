def test_root_returns_welcome_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from fastapi-blog!"}


def test_post_routes_are_versioned(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert set(response.json()["paths"]) == {
        "/api/v1/posts",
        "/api/v1/posts/{post_id}",
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
