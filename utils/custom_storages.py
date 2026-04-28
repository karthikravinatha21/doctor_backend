from django.core.files.storage import FileSystemStorage
from rest_framework import status
from storages.backends.s3boto3 import S3Boto3Storage
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError, APIException


# from utils.exceptions import ImageConvertTypeException

class ImageConvertTypeException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'error_while_image_convert'
    default_detail = 'Error while image convert to webp'

MANDATORY_FIELD_MISSING = "Mandatory Parameter missing"
class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

    def _is_image(self, content):
        return hasattr(content, 'content_type') and content.content_type.startswith('image/')

    def image_convert(self, name, content, *args, **kwargs):
        import io
        """
        Custom method to convert images to WebP format before saving.
        """
        try:
            # Open the image using PIL
            image = Image.open(content)

            # Convert the image to WebP format
            output = io.BytesIO()
            image.save(output, format='WEBP')
            name = name.rsplit('.', 1)[0] + '.webp'
            content = ContentFile(output.getvalue(), name=name)
            output.close()

            return name, content
        except Exception as e:
            raise Exception(f"Error converting image: {e}")

    def _save(self, name, content):
        """
        Save content using the parent storage backend.
        """
        return super()._save(name, content)

    def save(self, name, content, max_length=None):
        """
        Convert images to WebP and save using the generated key.
        """
        if self._is_image(content):
            name, content = self.image_convert(name, content)
        return super()._save(name, content)


class FileStorage(S3Boto3Storage):
    location = 'files'
    file_overwrite = False


class LocalFileStorage(FileSystemStorage):
    location = 'files'
    file_overwrite = True


class ImageHelpers:
    @staticmethod
    def convert_image_to_webp_formate(image, file_name):
        try:
            if image:
                image_bytes = image.read()
                image = Image.open(BytesIO(image_bytes))
                webp_image = BytesIO()
                image.save(webp_image, 'WEBP')
                return ContentFile(webp_image.getvalue(), name=f"{file_name}.webp")
        except ImageConvertTypeException:
            raise ImageConvertTypeException
        else:
            raise ValidationError(MANDATORY_FIELD_MISSING)
