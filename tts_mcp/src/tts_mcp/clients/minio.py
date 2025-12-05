# clients/minio.py

from minio import Minio
from minio.error import S3Error
from minio.lifecycleconfig import (
    LifecycleConfig,
    Rule,
    Expiration,
)
from minio.commonconfig import Filter
import json
import logging

class MinioClient:
    _bucket: str
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool, bucket: str, logger: logging.Logger = logging.getLogger(__name__)) -> None:
        self.logger = logger
        try:
            self.client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure,
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize MinIO client: {str(e)}")
            raise
        self._bucket = bucket

    # Bucket functions

    def create_bucket(self, bucket: str = None, expiration: int = 0, anonymous: bool = False) -> bool:
        bucket = bucket if bucket else self._bucket
        if self.client.bucket_exists(bucket_name=bucket):
            return False
        try:
            self.client.make_bucket(bucket_name=bucket)
            self.logger.info(f"Bucket '{bucket}' created.")
            if expiration > 0:
                self.set_bucket_policy_expiration(bucket=bucket, expiration=expiration)
            if anonymous:
                self.set_bucket_policy_anonymous_download(bucket=bucket, anonymous=anonymous)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create bucket '{bucket}': {str(e)}")
            return False
        
    def set_bucket_policy_expiration(self, bucket: str = None, expiration: int = 0) -> bool:
        bucket = bucket if bucket else self._bucket
        lifecycle_config = LifecycleConfig(
                [
                    Rule(
                        status="Enabled",
                        rule_filter=Filter(prefix=""),
                        expiration=Expiration(days=expiration),
                        rule_id=f"expire-all-{expiration}-days",
                    )
                ]
            )
        try:
            self.client.set_bucket_lifecycle(bucket_name=bucket, config=lifecycle_config)
            self.logger.info(f"Lifecycle set: delete files in '{bucket}' after {expiration} days.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set lifecycle for bucket '{bucket}': {str(e)}")
            return False

    def set_bucket_policy_anonymous_download(self, bucket: str = None, anonymous: bool = False) -> bool:
        bucket = bucket if bucket else self._bucket
        policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]}, # "AWS" is just syntax here, it means "Anyone"
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket}/*"] # Keep "aws:s3" prefix!
                        }
                    ]
                }
        try:
            self.client.set_bucket_policy(bucket_name=bucket, policy=json.dumps(policy))
            self.logger.info(f"Public read access enabled for '{bucket}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set public read access for bucket '{bucket}': {str(e)}")
            return False

    def delete_bucket(self, bucket: str = None, force: bool = False) -> bool:
        bucket = bucket if bucket else self._bucket
        try:
            if force:
                objects = self.client.list_objects(bucket_name=bucket, recursive=True)
                for obj in objects:
                    self.client.remove_object(bucket_name=bucket, object_name=obj.object_name)
                self.logger.info(f"Objects in bucket '{bucket}' deleted.")
            self.client.remove_bucket(bucket_name=bucket)
            self.logger.info(f"Bucket '{bucket}' deleted.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete bucket '{bucket}': {str(e)}")
            return False

    def exists_bucket(self, bucket: str = None) -> bool:
        bucket = bucket if bucket else self._bucket
        try:
            return self.client.bucket_exists(bucket_name=bucket)
        except Exception as e:
            self.logger.error(f"Failed to check if bucket '{bucket}' exists: {str(e)}")
            return False
    
    # File functions

    def upload_file(self, file_path: str, object_name: str = None, bucket: str = None) -> bool:
        bucket = bucket if bucket else self._bucket
        object_name = object_name[1:] if object_name.startswith("/") else object_name
        try:
            self.client.fput_object(bucket_name=bucket, object_name=object_name, file_path=file_path)
            self.logger.info(f"File '{file_path}' uploaded to '{bucket}' as '{object_name}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to upload file '{file_path}' to '{bucket}' as '{object_name}': {str(e)}")
            return False

    def download_file(self, object_name: str, file_path: str = None, bucket: str = None) -> bool:
        bucket = bucket if bucket else self._bucket
        object_name = object_name[1:] if object_name.startswith("/") else object_name
        try:
            self.client.fget_object(bucket_name=bucket, object_name=object_name, file_path=file_path)
            self.logger.info(f"File '{object_name}' downloaded from '{bucket}' to '{file_path}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download file '{object_name}' from '{bucket}' to '{file_path}': {str(e)}")
            return False

    def delete_file(self, object_name: str, bucket: str = None) -> bool:
        bucket = bucket if bucket else self._bucket
        object_name = object_name[1:] if object_name.startswith("/") else object_name
        try:
            self.client.remove_object(bucket_name=bucket, object_name=object_name)
            self.logger.info(f"File '{object_name}' deleted from '{bucket}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file '{object_name}' from '{bucket}': {str(e)}")
            return False

    def exists_file(self, object_name: str, bucket: str = None) -> bool:
        bucket = bucket if bucket else self._bucket
        object_name = object_name[1:] if object_name.startswith("/") else object_name
        try:
            return self.client.bucket_exists(bucket_name=bucket)
        except Exception as e:
            self.logger.error(f"Failed to check if file '{object_name}' exists in '{bucket}': {str(e)}")
            return False