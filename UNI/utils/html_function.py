from io import BytesIO  # A stream implementation using an in-memory bytes buffer
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

import boto3
AWS_STORAGE_BUCKET_NAME='masterclass-public'

def upload_pdf_S3(pdf):
   s3 = boto3.resource('s3')
   try:
       s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
           Key="new.pdf",
           Body=pdf)
       return True
   except:
       return False


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(html, result)
    upload_pdf_S3(result.getvalue())
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

