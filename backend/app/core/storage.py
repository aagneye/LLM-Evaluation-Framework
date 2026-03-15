import json
from typing import Optional, BinaryIO
from pathlib import Path
import structlog
import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class S3StorageManager:
    """S3-compatible storage manager for dataset uploads."""
    
    def __init__(self):
        self.s3_endpoint = getattr(settings, 's3_endpoint_url', None)
        self.s3_bucket = getattr(settings, 's3_bucket_name', 'llm-eval-datasets')
        self.s3_access_key = getattr(settings, 's3_access_key', None)
        self.s3_secret_key = getattr(settings, 's3_secret_key', None)
        
        self.client = None
        if self.s3_access_key and self.s3_secret_key:
            self.client = boto3.client(
                's3',
                endpoint_url=self.s3_endpoint,
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key
            )
    
    def is_available(self) -> bool:
        """Check if S3 storage is configured and available."""
        if not self.client:
            return False
        
        try:
            self.client.head_bucket(Bucket=self.s3_bucket)
            return True
        except Exception as e:
            logger.debug("s3_not_available", error=str(e))
            return False
    
    def upload_dataset(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/json"
    ) -> Optional[str]:
        """
        Upload a dataset file to S3.
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            content_type: MIME type
            
        Returns:
            S3 key/path or None if failed
        """
        if not self.is_available():
            logger.error("s3_upload_failed", reason="s3_not_configured")
            return None
        
        s3_key = f"datasets/{filename}"
        
        try:
            self.client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            
            logger.info("dataset_uploaded", filename=filename, s3_key=s3_key)
            return s3_key
            
        except ClientError as e:
            logger.error("s3_upload_failed", filename=filename, error=str(e))
            return None
    
    def download_dataset(self, s3_key: str) -> Optional[bytes]:
        """
        Download a dataset from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            File content as bytes or None
        """
        if not self.is_available():
            return None
        
        try:
            response = self.client.get_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            
            content = response['Body'].read()
            logger.info("dataset_downloaded", s3_key=s3_key, size=len(content))
            return content
            
        except ClientError as e:
            logger.error("s3_download_failed", s3_key=s3_key, error=str(e))
            return None
    
    def list_datasets(self, prefix: str = "datasets/") -> list[str]:
        """List all datasets in S3."""
        if not self.is_available():
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            keys = [obj['Key'] for obj in response.get('Contents', [])]
            logger.info("datasets_listed", count=len(keys))
            return keys
            
        except ClientError as e:
            logger.error("s3_list_failed", error=str(e))
            return []
    
    def delete_dataset(self, s3_key: str) -> bool:
        """Delete a dataset from S3."""
        if not self.is_available():
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            
            logger.info("dataset_deleted", s3_key=s3_key)
            return True
            
        except ClientError as e:
            logger.error("s3_delete_failed", s3_key=s3_key, error=str(e))
            return False


def get_storage_manager() -> S3StorageManager:
    """Get storage manager instance."""
    return S3StorageManager()
