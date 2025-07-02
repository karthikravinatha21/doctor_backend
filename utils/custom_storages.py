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
    file_overwrite = True

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
            content = io.BytesIO(output.getvalue())
            name = name.rsplit('.', 1)[0] + '.webp'
            output.close()

            # Save the processed image using the parent class's save method
            return super()._save(name, content)
        except Exception as e:
            raise Exception(f"Error converting image: {e}")

    def _save(self, name, content):
        """
        Override the _save method to include image conversion.
        """
        # Check if the file is an image
        if hasattr(content, 'content_type') and content.content_type.startswith('image/'):
            return self.image_convert(name, content)
        else:
            return super()._save(name, content)

    def save(self, name, content, max_length=None):
        """
        Override the save method to handle image conversion.
        """
        return self._save(name, content)


class FileStorage(S3Boto3Storage):
    location = 'files'
    file_overwrite = True


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

