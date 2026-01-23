def test_root_returns_200(client):
    """Test that root endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_signin_page(client):
    """Test that root endpoint returns the sign-in page."""
    response = client.get("/")
    assert "Class Portal" in response.text
    assert "email" in response.text.lower()
