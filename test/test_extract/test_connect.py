import pytest
from util_functions import connect
from unittest.mock import patch, MagicMock


def test_connect():
    """
    Test the `connect` function to ensure it retrieves secrets, creates a
    Connection object with the correct parameters, and returns the Connection instance.
    """
    # Mock the return value of get_secret
    mock_secret = {
        "user": "test_user",
        "database": "test_db",
        "password": "test_password",
        "host": "test_host",
        "port": 5432,
    }

    # Mock the Connection object
    mock_connection = MagicMock()

    with patch(
        "util_functions.get_secret", return_value=mock_secret
    ) as mock_get_secret, patch(
        "util_functions.Connection", return_value=mock_connection
    ) as mock_connection_cls:
        # Call the connect function
        connection = connect()

        mock_get_secret.assert_called_once_with("database_credentials")
        mock_connection_cls.assert_called_once_with(
            user="test_user",
            database="test_db",
            password="test_password",
            host="test_host",
            port=5432,
        )

        # Ensure the returned connection is the mocked one
        assert connection == mock_connection


import pytest


def test_connect_missing_key():
    """
    Test that `connect` raises a KeyError if any required key is missing
    in the secret dictionary returned by `get_secret`.
    """
    mock_secret = {
        "user": "test_user",
        "database": "test_db",
        # Missing "password", "host", "port"
    }

    with patch("util_functions.get_secret", return_value=mock_secret):
        with pytest.raises(KeyError, match="password"):
            connect()
