import boto3
import json
from moto import mock_aws
from util_functions import get_secret
from unittest.mock import patch
from botocore.exceptions import ClientError
import pytest


@mock_aws
def test_get_secret():
    """
    This test sets up a mock AWS Secrets Manager client, creates a secret with predefined values, and calls the get_secret function to ensure that it correctly retrieves the secret.

    The secret name and values are mocked, and the test verifies that the returned secret matches the mock values.

    Assumes the use of moto for mocking AWS services.

    Raises:
        AssertionError: If the retrieved secret does not match the expected mock values.
    """
    # Define the secret name and values
    mock_secret_name = "test-database-secret"
    region_name = "eu-west-2"
    mock_secret_values = {
        "user": "test-user",
        "database": "test-database",
        "password": "test-password",
        "host": "localhost",
        "port": "5432",
    }

    # Set up mock Secrets Manager
    mock_client = boto3.client("secretsmanager", region_name=region_name)
    mock_client.create_secret(
        Name=mock_secret_name, SecretString=json.dumps(mock_secret_values)
    )

    result = get_secret(secret_name=mock_secret_name)

    assert result == mock_secret_values


@mock_aws
def test_get_secret_missing_secret():
    """
    This test simulates a missing secret scenario by triggering a ResourceNotFoundException from the mocked Secrets Manager client. It ensures that the get_secret function raises a RuntimeError with a meaningful error message when the secret is not found.

    Assumes the use of moto for mocking AWS services.

    Raises:
        RuntimeError: If the secret is not found, indicating a failure to retrieve the secret.
    """
    secret_name = "nonexistent-secret"
    region_name = "us-east-1"

    # Mock boto3 client
    with patch("boto3.client") as mock_boto_client:
        mock_client = mock_boto_client.return_value

        # Simulate a ResourceNotFoundException
        mock_client.get_secret_value.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Secret not found",
                }
            },
            operation_name="GetSecretValue",
        )

        # Verify that the exception is raised with a meaningful error message
        with pytest.raises(RuntimeError, match="Failed to retrieve secret:"):
            get_secret(secret_name, region_name=region_name)
