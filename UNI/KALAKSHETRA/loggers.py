import datetime
from django.conf import settings

AWS_STORAGE_BUCKET_NAME = 'kalakshetra-dev-static-files'
today = datetime.datetime.utcnow().strftime('%Y-%m-%d')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname:^8}] {asctime} | {pathname}:{lineno} | {funcName}() | {message}',
            'style': '{',
        },
    },
    'handlers': {
        's3_info': {
            'level': 'INFO',
            'class': 'utils.s3_log_handler.S3LogHandler',
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'log_file_pattern': 'logs/info-{date}.log',
            'formatter': 'verbose',
        },
        's3_error': {
            'level': 'ERROR',
            'class': 'utils.s3_log_handler.S3LogHandler',
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'log_file_pattern': 'logs/error-{date}.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['s3_info', 's3_error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['s3_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['s3_error'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
