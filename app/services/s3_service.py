import boto3
from app.config import AWS_REGION, S3_BUCKET_NAME

s3 = boto3.client("s3", region_name=AWS_REGION)


def upload_to_s3(file) -> str:
    """Upload a file to S3 and return the S3 URI."""
    s3.upload_fileobj(file.file, S3_BUCKET_NAME, file.filename)
    return f"s3://{S3_BUCKET_NAME}/{file.filename}"


def get_presigned_url(filename: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed URL for temporary access to an S3 object."""
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": filename},
        ExpiresIn=expires_in
    )