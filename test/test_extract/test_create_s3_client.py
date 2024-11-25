from util_functions import create_s3_client
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import NoCredentialsError
import pytest
import boto3


@mock_aws
def test_create_s3_client_success():
    s3_client = create_s3_client()

    # Successfull creation of S3 client would have the method 'list_buckets'
    assert hasattr(s3_client, "list_buckets")


@patch("util_functions.boto3.client")
def test_create_s3_no_credentials(mock_boto_client):

    # Simulates an error caused by no credentials being provided
    mock_boto_client.side_effect = NoCredentialsError()

    with pytest.raises(NoCredentialsError):
        create_s3_client()
