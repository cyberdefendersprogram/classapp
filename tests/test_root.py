from unittest.mock import patch


def test_root_returns_200(client):
    """Test that root endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


@patch("app.routers.auth.get_sheets_client")
def test_root_returns_signin_page(mock_sheets, client):
    """Test that root endpoint returns the sign-in page."""
    mock_sheets.return_value.get_config.return_value = None

    response = client.get("/")
    assert "Class Portal" in response.text
    assert "email" in response.text.lower()
