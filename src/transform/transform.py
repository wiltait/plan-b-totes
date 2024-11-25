import boto3
import pandas as pd
from io import BytesIO
from datetime import datetime
import logging
from transform_utils import extract_files_from_event, load_raw_data, perform_transformations, save_transformed_data 


def lambda_handler(event, context):
    """
    Entry point for the Lambda function. Handles both S3-triggered events
    and batch processing scenarios.
    """
    logging.info("Starting transformation process.")
    
    # Determine if this is triggered by S3 or a batch job
    triggered_files = extract_files_from_event(event)

    # Load raw data
    raw_data = load_raw_data(triggered_files)

    # Perform transformations
    transformed_data = perform_transformations(raw_data)

    # Save transformed data back to S3
    save_transformed_data(transformed_data)

    logging.info("Data transformed and saved successfully.")
    return {"statusCode": 200, "body": "Data transformation complete."}
