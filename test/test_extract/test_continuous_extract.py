import pytest
from unittest.mock import patch, MagicMock
from extract import continuous_extract


@pytest.fixture
def mock_data():
    """Provide mock data for the tests."""
    return {
        "mock_table_data": [("table1",)],
        "mock_rows": [
            {"id": 1, "name": "Test", "created_at": "2024-01-01 00:00:00"},
            {"id": 2, "name": "Test2", "created_at": "2024-01-02 00:00:00"},
        ],
        "mock_columns": [{"name": "id"}, {"name": "name"}, {"name": "created_at"}],
    }


@pytest.fixture
def mock_s3_client():
    """Mock the S3 client for storing data."""
    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: "2024-01-01 00:00:00".encode("utf-8"))
    }
    return mock_s3


@pytest.fixture
def mock_db_connection(mock_data):
    """Mock the database connection."""
    mock_conn = MagicMock()
    mock_conn.run.side_effect = [
        mock_data["mock_table_data"],  # Response for table names query
        mock_data["mock_rows"],  # Response for data query
    ]
    mock_conn.columns = mock_data["mock_columns"]
    return mock_conn


@patch("util_functions.create_s3_client")
@patch("util_functions.connect")
def test_continuous_extract_successful_extraction(
    mock_connect, mock_create_s3_client, mock_s3_client, mock_db_connection
):
    """
    Test that continuous_extract successfully extracts data from the database and stores it in S3.
    Mocks the S3 client and database connection, simulating a successful extraction
    of data from the database and storing it in an S3 bucket.
    """
    # Set up mock S3 client and database connection
    mock_create_s3_client.return_value = mock_s3_client
    mock_connect.return_value = mock_db_connection

    # Call the function to test
    result = continuous_extract(mock_s3_client, mock_db_connection)

    # Assertions
    assert result == {"result": "Success"}

    # Ensure S3 'get_object' method was called with the correct arguments
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="banana-squad-code", Key="last_extracted.txt"
    )

    # Ensure that the database queries were called with correct SQL
    mock_db_connection.run.assert_any_call(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name != '_prisma_migrations'"
    )
    mock_db_connection.run.assert_any_call(
        "SELECT * FROM table1 WHERE created_at > '2024-01-01 00:00:00'"
    )

    # Ensure that the S3 store function was called with the correct parameters
    mock_s3_client.put_object.assert_called_once()
