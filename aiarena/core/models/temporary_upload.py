import uuid

from django.db import models

from botocore.exceptions import ClientError
from private_storage.fields import PrivateFileField

from .user import User


class TemporaryUpload(models.Model):
    """
    Tracks temporary file uploads to S3 until they are consumed by result submission.
    Records are deleted when the upload is used (copied to permanent location).
    """

    file = PrivateFileField(upload_to="temp-uploads/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="temporary_uploads")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TemporaryUpload({self.id}, {self.s3_key})"

    @property
    def _storage(self):
        return self.file.storage

    @property
    def _client(self):
        return self._storage.connection.meta.client

    @property
    def _bucket_name(self):
        return self._storage.bucket_name

    @property
    def s3_key(self):
        return self.file.name

    @classmethod
    def create_for_upload(cls, user: User) -> "TemporaryUpload":
        """Create a TemporaryUpload record with a generated S3 key."""
        upload = cls(uploaded_by=user)
        upload.file.name = f"temp-uploads/{uuid.uuid4().hex}"
        upload.save()
        return upload

    def generate_presigned_put_url(self) -> str:
        """Generate a presigned PUT URL for direct S3 upload."""
        return self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": self.s3_key,
            },
            ExpiresIn=3600,
        )

    def copy_to(self, dest_key: str) -> None:
        """Copy to permanent location. Does not delete the source."""
        self._client.copy_object(
            Bucket=self._bucket_name,
            CopySource={"Bucket": self._bucket_name, "Key": self.s3_key},
            Key=dest_key,
        )

    def copy_to_file_field(self, file_field, filename: str) -> None:
        """
        Copy the uploaded file to a model's FileField.

        Uses S3-to-S3 copy (no data through the web worker), then sets the field's
        name to the destination key.
        """
        if not self.exists_in_s3():
            raise ValueError("Upload not found in S3")
        dest_key = file_field.field.upload_to(file_field.instance, filename)
        self.copy_to(dest_key)
        file_field.name = dest_key

    def delete_s3_object(self) -> None:
        """Delete the S3 object."""
        self._client.delete_object(Bucket=self._bucket_name, Key=self.s3_key)

    def exists_in_s3(self) -> bool:
        """Check if the file was actually uploaded to S3."""
        try:
            self._client.head_object(Bucket=self._bucket_name, Key=self.s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
