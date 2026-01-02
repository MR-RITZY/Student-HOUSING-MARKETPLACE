import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile
from typing import List
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256


from src.stu_house_market.core.config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.B2_S3_ENDPOINT}",
    aws_access_key_id=settings.B2_APP_KEY_ID,
    aws_secret_access_key=settings.B2_APP_KEY,
    config=Config(signature_version="s3v4"),
)


def ensure_bucket_exists():
    try:
        s3_client.head_bucket(Bucket=settings.B2_BUCKET)
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in ("404", "NoSuchBucket"):
            s3_client.create_bucket(Bucket=settings.B2_BUCKET)
            return True

        return False


def upload_files(file_objs: List[UploadFile], user_id: str):
    hashed_user_id = sha256(user_id.encode(), usedforsecurity=True).hexdigest()

    def _upload(file_obj: UploadFile):
        filename = f"usr_{hashed_user_id}/{uuid4()}_{file_obj.filename}"
        s3_client.upload_fileobj(file_obj.file, settings.B2_BUCKET, filename)
        return filename

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(_upload, file_objs))

    return results


def generate_presigned_upload_urls(image_count: int):
    urls = []
    for _ in range(image_count):
        file_key = f"house/{uuid4()}.png"

        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.B2_BUCKET,
                "Key": file_key,
                "ContentType": "image/png",
            },
            ExpiresIn=3600,
        )

        urls.append({"upload_url": url, "file_key": file_key})

    return urls


def generate_presigned_download_urls(file_keys: List[str]):
    urls = []
    for file_key in file_keys:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.B2_BUCKET,
                "Key": file_key,
                "ContentType": "image/png",
            },
            ExpiresIn=3600,
        )
        if url:
            urls.append({"download_url": url, "file_key": file_key})
    return urls
