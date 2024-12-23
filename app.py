oto3
import os
import zipfile
import pymysql
import csv
import io
from botocore.exceptions import ClientError

# AWS configuration
S3_BUCKET_NAME = "my-data-bucket-03"  # Replace with your S3 bucket name
AWS_REGION = "us-east-1"  # Ensure this matches your Terraform setup
CSV_FILE_NAME = "/tmp/users.csv"  # Use /tmp for writable files in AWS Lambda
ZIP_FILE_NAME = "/tmp/users.zip"  # Use /tmp for the ZIP file

# RDS Configuration
RDS_HOST = 'rds-instance.cdc4yye8yku4.us-east-1.rds.amazonaws.com'  # Replace with your RDS endpoint
RDS_USER = 'admin'  # Replace with your RDS username
RDS_PASSWORD = 'password123'  # Replace with your RDS password
RDS_DATABASE = 'data_pipeline'  # Replace with your RDS database name
RDS_TABLE = 'my_users'  # Replace with your RDS table name

# AWS Glue Configuration
AWS_GLUE_DATABASE = 'fallback_database'  # Replace with your Glue database name
AWS_GLUE_TABLE = 'user_backup'  # Replace with your Glue table name

# Create sample data for testing
def create_sample_csv(file_name):
    data = [
        "name,email",
        "Ankit,patilankit03@gmail.com",
        "Abhi,abhiwahurwagh04@gmail.com",
        "Charlie,charlie05@gmail.com"
    ]
    try:
        with open(file_name, "w") as file:
            file.write("\n".join(data))
        print(f"CSV file created: {file_name}")
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        raise

# Zip the CSV file
def zip_file(file_name, zip_file_name):
    try:
        if os.path.exists(file_name):
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_name, os.path.basename(file_name))
            print(f"File {file_name} zipped as {zip_file_name}")
        else:
            print(f"Error: File {file_name} does not exist. Cannot zip.")
            raise FileNotFoundError(f"{file_name} not found")
    except Exception as e:
        print(f"Error zipping file: {e}")
        raise

# Upload the ZIP file to S3
def upload_to_s3(bucket_name, file_name, s3_key):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        s3_client.upload_file(file_name, bucket_name, s3_key)
        print(f"File {file_name} successfully uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise

# Function to push data to RDS
def push_to_rds(csv_data):
    try:
        sanitized_data = csv_data.replace('\x00', '')  # Remove null characters, if any
        connection = pymysql.connect(
            host=RDS_HOST,
            port=3306,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DATABASE
        )
        cursor = connection.cursor()

        # Use csv.reader with universal newline support
        csv_reader = csv.reader(io.StringIO(sanitized_data), skipinitialspace=True)
        header = next(csv_reader)  # Skip the header

        # Insert each row into the RDS database
        for row in csv_reader:
            if len(row) != 2:  # Ensure each row has exactly 2 columns (name and email)
                print(f"Skipping malformed row: {row}")
                continue
            name = row[0].strip()
            email = row[1].strip()

            sql_query = f"INSERT INTO {RDS_TABLE} (name, email) VALUES (%s, %s)"
            cursor.execute(sql_query, (name, email))

        # Commit and close connection
        connection.commit()
        cursor.close()
        connection.close()

        print("Data successfully pushed to RDS!")
    except Exception as e:
        print(f"Error pushing data to RDS: {e}")
        raise

# Function to push data to AWS Glue
def push_to_glue(s3_key):
    glue_client = boto3.client('glue', region_name=AWS_REGION)
    try:
        response = glue_client.start_job_run(
            JobName='my-glue-job',  # Replace with your Glue job name
            Arguments={
                '--s3_input_path': f"s3://{S3_BUCKET_NAME}/{s3_key}",
                '--glue_database': AWS_GLUE_DATABASE,
                '--glue_table': AWS_GLUE_TABLE
            }
        )
        print(f"AWS Glue job started successfully: {response}")
    except Exception as e:
        print(f"Error triggering Glue job: {e}")
        raise

# Function to get the CSV data from S3
def get_s3_data(bucket, key):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8', 'ignore')  # Use 'ignore' to skip undecodable characters
        return file_content
    except Exception as e:
        print(f"Error getting object {key} from bucket {bucket}: {e}")
        return None

if __name__ == "__main__":
    try:
        # Generate the sample CSV file
        create_sample_csv(CSV_FILE_NAME)

        # Zip the CSV file
        zip_file(CSV_FILE_NAME, ZIP_FILE_NAME)

        # Upload the ZIP file to S3 bucket
        s3_key = os.path.basename(ZIP_FILE_NAME)
        upload_to_s3(S3_BUCKET_NAME, ZIP_FILE_NAME, s3_key)

        # Step 1: Get the CSV file content from S3
        csv_data = get_s3_data(S3_BUCKET_NAME, s3_key)

        if csv_data:
            # Step 2: Try pushing to RDS
            try:
                push_to_rds(csv_data)
            except Exception:
                print("RDS push failed. Falling back to Glue...")
                # Step 3: If RDS fails, push to Glue
                push_to_glue(s3_key)

    except Exception as e:
        print(f"An error occurred: {e}")
