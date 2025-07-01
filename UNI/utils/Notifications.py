import json

import requests
from apps.notifications.models import UserNotification
from apps.notifications.tasks import send_fcm_push_notification, send_ses_email
from django.conf import settings
from fcm_django.models import FCMDevice
from user_details.models import NotificationBlockList, User


class EmailnotifyClass():

    @classmethod
    def send_email(cls, subject=None, text_content=None, recepients=None,
                   bcc_recipients=[], html_content=None, attachment=None,
                   file_attachments=None):

        return send_ses_email.delay(
            subject=subject, text_content=text_content, bcc_recipients=bcc_recipients,
            file_attachments=file_attachments, recepients=recepients,
            html_content=html_content, attachments=attachment)


class FCMNoticicationsClass():
    def __init__(self, user=None):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + settings.FCM_SERVER_KEY
        }
        self.create_topic_endpoint = 'https://iid.googleapis.com/iid/v1:batchAdd'
        self.send_push_notification_endpoint = 'https://fcm.googleapis.com/fcm/send'
        blocked_objs = NotificationBlockList.objects.all().values_list('user_id', flat=True)
        blocked_user_obj = User.objects.filter(id__in=blocked_objs)
        self.fcm_devices = FCMDevice.objects.exclude(
            user_id__in=blocked_user_obj)
        # if user:
        #     self.fcm_devices = self.fcm_devices.filter(user=user, active=True)

    @classmethod
    def create_topic(cls, topic=None, user=None):
        obj = FCMNoticicationsClass(user=user)

        registration_tokens = list(
            obj.fcm_devices.values_list('registration_id', flat=True))

        payload = json.dumps(
            {
                "to": '/topics/' + topic,
                "registration_tokens": registration_tokens
            }
        )

        response = requests.request(
            "POST", obj.create_topic_endpoint, headers=obj.headers, data=payload)

        if response.status_code == 200:
            return True

        return False

    @classmethod
    def send_push_notification(cls, topic=None, user=None, users_list=[], notification_obj=None,
                               title=None, body=None, data_url=None, data_dl=None, newFeeds=False,
                               action_screen_value=None):
        obj = FCMNoticicationsClass()

        payload = {
            "notification": {
                "title": title,
                "body": body,
                "mutable_content": False,
                # "sound": "Tri-tone"
            }
        }

        # user_notification_objs = []
        blocked_users = NotificationBlockList.objects.all().values_list('user_id', flat=True)
        blocked_user_list = set(blocked_users)
        if user and user.id in blocked_user_list:
            return False

        if notification_obj:
            if user:
                created_user_notification_obj = UserNotification.objects.create(
                    notification=notification_obj,
                    user=user, message=body,
                    action_screen_type=notification_obj.action_screen_type,
                    action_screen_value=action_screen_value,
                    action_type=notification_obj.action_type
                )
                # user_notification_objs.append(
                #     created_user_notification_obj)
            if users_list:
                users_list = list(set(users_list) - blocked_user_list)
                for each_user in users_list:
                    created_user_notification_obj = UserNotification.objects.create(
                        notification=notification_obj,
                        user=User.objects.get(id=each_user), message=body,
                        action_screen_type=notification_obj.action_screen_type,
                        action_screen_value=action_screen_value,
                        action_type=notification_obj.action_type
                    )
                    # user_notification_objs.append(
                    #     created_user_notification_obj)

        if user and obj.fcm_devices.filter(
                user=user, active=True).exists():
            payload["to"] = obj.fcm_devices.filter(
                user=user, active=True).first().registration_id

        elif topic:
            payload["to"] = '/topics/' + topic

        elif obj.fcm_devices.filter(
                user__in=users_list, active=True).exists():
            payload["registration_ids"] = [each.registration_id for each in obj.fcm_devices.filter(
                user__in=users_list, active=True)]

        if 'to' in payload or 'topic' in payload or 'registration_ids' in payload:

            if data_url or data_dl or newFeeds:
                # url - url of media image
                # dl - deeplink action on tap of notification
                payload["data"] = {
                    "url": data_url,
                    "dl": data_dl,
                    "newFeeds": newFeeds
                }

            send_fcm_push_notification.delay(
                endpoint=str(obj.send_push_notification_endpoint),
                headers=obj.headers, payload=json.dumps(payload))

        return True
