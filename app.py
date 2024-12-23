import boto3
import os
import zipfile

# AWS S3 configuration
S3_BUCKET_NAME = "my-data-bucket-03"  # Replace with your S3 bucket name
AWS_REGION = "us-east-1"  # Ensure this matches your Terraform setup
CSV_FILE_NAME = "/tmp/users.csv"  # Use /tmp for writable files in AWS Lambda
ZIP_FILE_NAME = "/tmp/users.zip"  # Use /tmp for the ZIP file

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

if __name__ == "__main__":
    try:
        # Generate the sample CSV file
        create_sample_csv(CSV_FILE_NAME)

        # Zip the CSV file
        zip_file(CSV_FILE_NAME, ZIP_FILE_NAME)

        # Upload the ZIP file to the S3 bucket
        upload_to_s3(S3_BUCKET_NAME, ZIP_FILE_NAME, os.path.basename(ZIP_FILE_NAME))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup local files
        try:
            if os.path.exists(CSV_FILE_NAME):
                os.remove(CSV_FILE_NAME)
                print(f"Deleted: {CSV_FILE_NAME}")
            if os.path.exists(ZIP_FILE_NAME):
                os.remove(ZIP_FILE_NAME)
                print(f"Deleted: {ZIP_FILE_NAME}")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")
