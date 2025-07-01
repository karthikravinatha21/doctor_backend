import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

class S3LogHandler(logging.Handler):
    def __init__(self, bucket_name, log_file_pattern, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = bucket_name
        self.log_file_pattern = log_file_pattern  # e.g., 'logs/info-{date}.log'
        self.s3 = boto3.client('s3')

    def emit(self, record):
        try:
            log_message = self.format(record)

            # Replace {date} in pattern with today's date
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            log_file = self.log_file_pattern.format(date=date_str)

            # Fetch existing logs from S3 if any
            try:
                obj = self.s3.get_object(Bucket=self.bucket_name, Key=log_file)
                current_data = obj['Body'].read().decode('utf-8')
            except self.s3.exceptions.NoSuchKey:
                current_data = ""

            updated_data = current_data + log_message + "\n"

            # Upload updated log file back to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=log_file,
                Body=updated_data.encode('utf-8')
            )

        except ClientError as e:
            print(f"Error uploading log to S3: {e}")
        except Exception:
            self.handleError(record)
