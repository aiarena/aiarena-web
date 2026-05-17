import uuid

from django.db import models

from private_storage.fields import PrivateFileField
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name

from .user import User


class TemporaryUpload(models.Model):
    """
    Tracks temporary file uploads until they are consumed by result submission.
    Records are deleted when the upload is used (copied to permanent location).
    """

    file = PrivateFileField(upload_to="temp-uploads/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="temporary_uploads")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TemporaryUpload({self.id}, {self.file.name})"

    @classmethod
    def create_for_upload(cls, user: User) -> "TemporaryUpload":
        """Create a TemporaryUpload record with a storage-generated path."""
        upload = cls(uploaded_by=user)
        upload.file.name = cls._meta.get_field("file").generate_filename(upload, f"{uuid.uuid4().hex}")
        upload.save()
        return upload

    def generate_presigned_put_url(self) -> str:
        """Generate a presigned PUT URL for direct S3 upload.

        Only meaningful on S3 storage; dev/test environments don't presign.
        """
        storage = self.file.storage
        if not isinstance(storage, S3Boto3Storage):
            raise RuntimeError("Presigned URLs are only supported on S3 storage")
        # Storage prepends `location` (e.g. "private-media/") to the field name when
        # talking to S3; raw boto3 doesn't know that, so apply the same transform.
        s3_key = storage._normalize_name(clean_name(self.file.name))
        return storage.connection.meta.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": storage.bucket.name, "Key": s3_key},
            ExpiresIn=3600,
        )

    def exists_in_storage(self) -> bool:
        return self.file.storage.exists(self.file.name)

    def copy_to_file_field(self, dest_file_field, filename: str) -> None:
        """Copy the uploaded file into a model's FileField via S3-to-S3 copy."""
        if not self.exists_in_storage():
            raise ValueError("Upload not found in storage")

        src_storage = self.file.storage
        dst_storage = dest_file_field.storage

        if not (isinstance(src_storage, S3Boto3Storage) and isinstance(dst_storage, S3Boto3Storage)):
            raise RuntimeError("copy_to_file_field requires S3 storage on both source and destination")
        if src_storage.bucket.name != dst_storage.bucket.name:
            raise RuntimeError("Cross-bucket copy is not supported")

        # Build the destination name through the field's upload_to and storage,
        # so any path transforms (location prefix, name conflict resolution) apply.
        dest_name = dest_file_field.field.generate_filename(dest_file_field.instance, filename)

        client = src_storage.connection.meta.client
        client.copy_object(
            Bucket=dst_storage.bucket.name,
            CopySource={
                "Bucket": src_storage.bucket.name,
                "Key": src_storage._normalize_name(clean_name(self.file.name)),
            },
            Key=dst_storage._normalize_name(clean_name(dest_name)),
        )
        dest_file_field.name = dest_name

    def delete_from_storage(self) -> None:
        self.file.storage.delete(self.file.name)
