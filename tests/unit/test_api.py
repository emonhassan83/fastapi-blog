def test_root_returns_welcome_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from fastapi-blog!"}


def test_get_posts_returns_seed_posts(client):
    response = client.get("/posts")

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == 1
