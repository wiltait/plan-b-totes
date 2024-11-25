import boto3
import pandas as pd
from io import BytesIO
from datetime import datetime
import logging

# Initialize S3 client and logger
s3 = boto3.client('s3')
logging.basicConfig(level=logging.INFO)

# Define source and target S3 buckets
SOURCE_BUCKET = 'will-ingested-data-bucket'
TARGET_BUCKET = 'will-processed-data-bucket'

# Define table names
TABLES = [
    'sales_order', 'design', 'address', 'counterparty', 'transaction', 
    'payment', 'payment_type', 'staff', 'currency', 'department', 'purchase_order'
]

def extract_files_from_event(event):
    """
    Extracts file paths from an S3-triggered event or defaults to processing all tables.
    """
    if 'Records' in event:
        files = [
            {
                'bucket': record['s3']['bucket']['name'],
                'key': record['s3']['object']['key']
            }
            for record in event['Records']
        ]
        logging.info(f"Triggered by S3 event for files: {files}")
        return files
    else:
        # Default to processing all tables in batch mode
        logging.info("No S3 event detected; falling back to batch processing.")
        return [{"bucket": SOURCE_BUCKET, "key": f"{table}/"} for table in TABLES]

def load_raw_data(triggered_files):
    """
    Loads raw data from S3 for the specified files or tables.
    """
    raw_data = {}
    for file in triggered_files:
        table_name = file['key'].split('/')[0]  # Extract table name from the key
        raw_data[table_name] = load_table_from_s3(file['bucket'], file['key'])
    return raw_data

def load_table_from_s3(bucket, prefix):
    """
    Loads all CSV files from the specified bucket and prefix into a DataFrame.
    """
    files = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in files:
        logging.warning(f"No files found under prefix: {prefix}")
        return pd.DataFrame()

    dataframes = []
    for file in files['Contents']:
        file_key = file['Key']
        if file_key.endswith('.csv'):
            logging.info(f"Loading file: {file_key}")
            obj = s3.get_object(Bucket=bucket, Key=file_key)
            df = pd.read_csv(BytesIO(obj['Body'].read()))
            dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

def perform_transformations(raw_data):
    """
    Performs transformations for all tables.
    """
    transformed_data = {}
    
    # Existing transformations
    transformed_data['dim_date'] = transform_dim_date(raw_data.get('sales_order', pd.DataFrame()))
    transformed_data['dim_staff'] = transform_dim_staff(
        raw_data.get('staff', pd.DataFrame()), 
        raw_data.get('department', pd.DataFrame())
    )
    
    # Additional transformations
    transformed_data['dim_counterparty'] = transform_dim_counterparty(raw_data.get('counterparty', pd.DataFrame()))
    transformed_data['dim_currency'] = transform_dim_currency(raw_data.get('currency', pd.DataFrame()))
    transformed_data['dim_transaction'] = transform_dim_transaction(
        raw_data.get('transaction', pd.DataFrame()), 
        raw_data.get('payment', pd.DataFrame())
    )
    transformed_data['dim_address'] = transform_dim_address(raw_data.get('address', pd.DataFrame()))
    
    return transformed_data


def save_transformed_data(transformed_data):
    """
    Saves transformed data back to S3 as Parquet files.
    """
    for table_name, dataframe in transformed_data.items():
        if not dataframe.empty:
            save_to_s3(dataframe, table_name)
        else:
            logging.warning(f"No data to save for {table_name}.")

def save_to_s3(dataframe, table_name):
    """
    Saves a DataFrame as a Parquet file to the target S3 bucket.
    """
    buffer = BytesIO()
    dataframe.to_parquet(buffer, index=False)
    buffer.seek(0)

    file_key = f"{table_name}/{datetime.utcnow().strftime('%Y/%m/%d')}/{table_name}.parquet"
    logging.info(f"Saving transformed data to: {file_key}")
    s3.put_object(Bucket=TARGET_BUCKET, Key=file_key, Body=buffer.getvalue())

# --- Transformation Functions ---

def transform_dim_date(sales_order_df):
    """
    Example transformation: Creates dim_date table from sales_order data.
    """
    if sales_order_df.empty:
        logging.warning("Sales order data is empty; skipping dim_date transformation.")
        return pd.DataFrame()

    dim_date = sales_order_df[['order_date']].drop_duplicates()
    dim_date['year'] = pd.to_datetime(dim_date['order_date']).dt.year
    dim_date['month'] = pd.to_datetime(dim_date['order_date']).dt.month
    return dim_date

def transform_dim_staff(staff_df, department_df):
    """
    Creates dim_staff table by joining staff and department data.
    """
    if staff_df.empty or department_df.empty:
        logging.warning("Staff or department data is empty; skipping dim_staff transformation.")
        return pd.DataFrame()

    dim_staff = staff_df.merge(
        department_df[['department_id', 'department_name', 'location', 'manager']],
        on='department_id', how='left'
    )
    
    return dim_staff[['staff_id', 'first_name', 'last_name', 'department_name', 'location', 'email_address']]

def transform_dim_counterparty(counterparty_df):
    """
    Creates dim_counterparty table from counterparty data.
    """
    if counterparty_df.empty:
        logging.warning("Counterparty data is empty; skipping dim_counterparty transformation.")
        return pd.DataFrame()

    dim_counterparty = counterparty_df[['counterparty_id', 'name', 'address_id', 'phone_number']].drop_duplicates()
    return dim_counterparty

def transform_dim_currency(currency_df):
    """
    Creates dim_currency table from currency data.
    """
    if currency_df.empty:
        logging.warning("Currency data is empty; skipping dim_currency transformation.")
        return pd.DataFrame()

    dim_currency = currency_df[['currency_id', 'currency_code', 'description']].drop_duplicates()
    return dim_currency

def transform_dim_transaction(transaction_df, payment_df):
    """
    Creates dim_transaction table by combining transaction and payment data.
    """
    if transaction_df.empty or payment_df.empty:
        logging.warning("Transaction or payment data is empty; skipping dim_transaction transformation.")
        return pd.DataFrame()

    dim_transaction = transaction_df.merge(
        payment_df[['payment_id', 'amount', 'payment_type_id']],
        on='transaction_id', how='left'
    )
    
    return dim_transaction[['transaction_id', 'payment_id', 'amount', 'payment_type_id', 'timestamp']]

def transform_dim_address(address_df):
    """
    Creates dim_address table from address data.
    """
    if address_df.empty:
        logging.warning("Address data is empty; skipping dim_address transformation.")
        return pd.DataFrame()

    dim_address = address_df[['address_id', 'street', 'city', 'state', 'zip_code', 'country']].drop_duplicates()
    return dim_address