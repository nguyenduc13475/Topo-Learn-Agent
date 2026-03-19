import os
import shutil

import boto3

from app.core.config import settings


class S3Service:
    def __init__(self):
        self.is_local = settings.S3_ENDPOINT_URL == "placeholder"
        self.bucket = settings.S3_BUCKET_NAME

        if not self.is_local:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )

    def upload_file(self, file_path: str, file_type: str) -> str:
        """Uploads a local file to S3 or falls back to local static serving."""
        filename = os.path.basename(file_path)
        content_type = "application/pdf" if file_type == "pdf" else "video/mp4"

        if self.is_local:
            # Fallback: Copy file to a static serving directory
            serve_dir = "data/uploads/served"
            os.makedirs(serve_dir, exist_ok=True)
            target_path = os.path.join(serve_dir, filename)
            shutil.copy(file_path, target_path)
            # Return local API path (mounted in main.py)
            return f"/api/v1/static/uploads/{filename}"

        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket,
                filename,
                ExtraArgs={"ContentType": content_type},
            )
            # Safely join the domain and filename to prevent double slashes
            domain = settings.S3_PUBLIC_DOMAIN.rstrip("/")
            return f"{domain}/{filename}"
        except Exception as e:
            print(f"[S3 Service] Upload failed: {e}")
            raise e

    def delete_file(self, file_url: str):
        """Extracts filename from URL and deletes it from storage."""
        if not file_url:
            return

        filename = file_url.split("/")[-1]

        if self.is_local:
            target_path = os.path.join("data/uploads/served", filename)
            if os.path.exists(target_path):
                os.remove(target_path)
            return

        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=filename)
            print(f"[S3 Service] Deleted {filename} from bucket.")
        except Exception as e:
            print(f"[S3 Service] Delete failed: {e}")


s3_service = S3Service()
