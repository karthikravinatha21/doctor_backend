import datetime
import json
import requests
from django.conf import settings


def send_message_to_space(paylaod, error, type, response, url, method, alert=None):
    CHAT_BOT_WEBHOOK_URL = 'https://chat.googleapis.com/v1/spaces/AAAApNQyxhw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=YY8s4-gGoRSHm_hPrS8mxtgWq-rM-_qLCjjckOLOHZ8'
    ENV = "DEV"#settings.CHAT_BOT_ENV
    """
    If any issue in creating the payment link, its will be notifying to the BED dev space
    """
    # log_data = [
    #     f"info|| {datetime.datetime.now()}: Send SMS to space"]
    try:

        # Message to be sent with formatting
        message = {
            'cards': [
                {
                    'header': {
                        'title': f'<b style="color:red">Alert: {alert} Error in {type} &#9888;</b>',
                        'subtitle': f'{ENV} Environment'
                    },
                    'sections': [
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">Payload:</b> {str(paylaod)}'
                                    }
                                }
                            ]
                        },
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">Response:</b> {str(response)}'
                                    }
                                }
                            ]
                        },
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">Error:</b> {str(error)}'
                                    }
                                }
                            ]
                        },
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">URL:</b> {str(url)}'
                                    }
                                }
                            ]
                        },
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">Method:</b> {str(method)}'
                                    }
                                }
                            ]
                        },
                        {
                            'widgets': [
                                {
                                    'textParagraph': {
                                        'text': f'<b style="color:red">DATE:</b> {str(datetime.datetime.now().strftime("%b %d %Y %I:%M %p"))}'
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        # Convert the message to JSON format
        message_json = json.dumps(message)

        # Send the POST request to the webhook URL
        response = requests.post(CHAT_BOT_WEBHOOK_URL, data=message_json, timeout=30)
    except Exception as e:
        print(e)
        # context = {
        #     "paylaod": paylaod, "error": e, "error_from_response": error}
        # log_data.append(f"info || Send SMS to space :{context}")
        # log_data.append(LINE_BREAK)
        # api_logging(log_data)
