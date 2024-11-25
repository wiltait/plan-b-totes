from extract import lambda_handler
from moto import mock_aws
from botocore.exceptions import NoCredentialsError, ClientError
from pg8000.exceptions import InterfaceError, DatabaseError
from unittest.mock import patch, MagicMock
from datetime import datetime
import unittest
import pytest
import boto3


@mock_aws
@patch("extract.create_s3_client")
@patch("extract.connect")
@patch("extract.initial_extract")
@patch("extract.continuous_extract")
def test_continuous_extract_called_when_last_extracted_exists(
    mock_continuous, mock_initial, mock_connect, mock_s3_client
):
    secret_name = "database_credentials"
    region_name = "eu-west-2"
    client = boto3.client("secretsmanager", region_name=region_name)
    client.create_secret(
        Name=secret_name,
        SecretString='{"user":"test_user","database":"test_db","password":"test_pass","host":"localhost","port":"5432"}',
    )

    mock_s3 = MagicMock()
    mock_s3.list_objects.return_value = {"Contents": [{"Key": "last_extracted.txt"}]}
    mock_s3_client.return_value = mock_s3

    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    result = lambda_handler({}, {})

    mock_continuous.assert_called_once_with(mock_s3, mock_conn)
    mock_initial.assert_not_called()

    assert result["result"] == "Success"


@mock_aws
@patch("extract.connect")
@patch("extract.create_s3_client")
@patch("extract.initial_extract")
@patch("extract.continuous_extract")
def test_initial_extract_called_when_last_extracted_missing(
    mock_continuous, mock_initial, mock_s3_client, mock_connect
):
    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.list_objects.return_value = {}  # Simulate missing file
    mock_s3_client.return_value = mock_s3

    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    result = lambda_handler({}, {})

    mock_initial.assert_called_once_with(mock_s3, mock_conn)
    mock_continuous.assert_not_called()

    assert result["result"] == "Success"


@patch("extract.create_s3_client")
def test_no_credentials_error(mock_create_s3_client):

    mock_create_s3_client.side_effect = NoCredentialsError

    result = lambda_handler({}, {})

    assert result["result"] == "Failure"
    assert result["error"] == "AWS credentials not found. Unable to create S3 client"


@patch("extract.create_s3_client")
def test_client_error_during_s3_creation(mock_create_s3_client):

    mock_create_s3_client.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "ListBuckets"
    )

    result = lambda_handler({}, {})

    assert result["result"] == "Failure"
    assert result["error"] == "Error creating S3 client"


@patch("extract.create_s3_client")
def test_client_error_during_s3_creation(mock_create_s3_client):

    mock_create_s3_client.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "CreateS3Client",
    )

    result = lambda_handler(event={}, context={})

    assert result["result"] == "Failure"
    assert "Error creating S3 client" in result["error"]


@patch("extract.connect")
@patch("extract.create_s3_client")
def test_unexpected_error_during_put_object(mock_create_s3_client, mock_conn):

    mock_conn = MagicMock()
    mock_s3_client = mock_create_s3_client.return_value
    mock_put_object = mock_s3_client.put_object
    mock_put_object.side_effect = Exception("Unexpected error occurred")

    result = lambda_handler(event={}, context={})

    assert result["result"] == "Failure"
    assert "Unexpected error" in result["error"]
