from extract import initial_extract
import pytest
from unittest.mock import patch, MagicMock, call
from io import StringIO


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
def test_initial_extract_successful_extraction(
    mock_connect, mock_create_s3_client, mock_data, mock_s3_client, mock_db_connection
):
    # Set up mock S3 client and database connection
    mock_create_s3_client.return_value = mock_s3_client
    mock_connect.return_value = mock_db_connection

    # Call the function to test
    result = initial_extract(mock_s3_client, mock_db_connection)

    # Assertions
    assert result == {"result": "Success"}

    # Ensure that the S3 store function was called with the correct parameters
    mock_s3_client.put_object.assert_called_once()


@patch("util_functions.create_s3_client")
@patch("util_functions.connect")
def test_initial_extract_s3_upload_failure(
    mock_connect, mock_create_s3_client, mock_data, mock_s3_client, mock_db_connection
):
    # Simulate an exception during S3 upload
    mock_s3_client.put_object.side_effect = Exception("S3 upload failed")
    mock_create_s3_client.return_value = mock_s3_client
    mock_connect.return_value = mock_db_connection

    # Test that the exception is raised
    with pytest.raises(Exception, match="S3 upload failed"):
        initial_extract(mock_s3_client, mock_db_connection)

    # Ensure that the S3 store function was called
    mock_s3_client.put_object.assert_called_once()


@patch("util_functions.create_s3_client")
@patch("util_functions.connect")
def test_initial_extract_table_with_no_rows(
    mock_connect, mock_create_s3_client, mock_s3_client, mock_db_connection, mock_data
):
    mock_create_s3_client.return_value = mock_s3_client
    mock_connect.return_value = mock_db_connection

    # Mock one table and an empty rows response
    mock_db_connection.run.side_effect = [mock_data["mock_table_data"], []]
    mock_db_connection.columns = mock_data["mock_columns"]

    result = initial_extract(mock_s3_client, mock_db_connection)

    assert result == {"result": "Success"}
    mock_s3_client.put_object.assert_not_called()


def test_initial_extract_no_rows(mock_data, mock_s3_client, mock_db_connection):
    # Modify mock to return empty rows
    mock_db_connection.run.side_effect = [
        mock_data["mock_table_data"],  # Table names
        [],  # Empty rows for a table
    ]

    # Call function, ensure no errors
    result = initial_extract(mock_s3_client, mock_db_connection)
    assert result == {"result": "Success"}


def test_initial_extract_multiple_tables(mock_data, mock_s3_client, mock_db_connection):
    # Modify mock to return multiple tables
    mock_data["mock_table_data"] = [("table1",), ("table2",)]
    mock_db_connection.run.side_effect = [
        mock_data["mock_table_data"],  # Table names
        mock_data["mock_rows"],  # Rows for first table
        mock_data["mock_rows"],  # Rows for second table
    ]

    # Call function
    result = initial_extract(mock_s3_client, mock_db_connection)
    assert result == {"result": "Success"}
