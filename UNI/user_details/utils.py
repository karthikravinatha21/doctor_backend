from apps.notifications.models import NotificationMaster
from utils.adaptor import template_to_fcm_message
from utils.Notifications import FCMNoticicationsClass

from .models import UserInterests


def calculate_profile_complete_percentage(user_obj=None):
    # ......................
    # mobile number : 20%
    # .....................
    # email
    # name
    # gender
    # 20%
    # ................................

    # university
    # passout year
    # course

    # 20%
    # ..................................
    # carreer interest 20%  - minimum any one interest
    # .......................................
    # persoanal interest 20% - minimum any one interest

    percentage = 0

    if user_obj.mobile:
        percentage += 20

    if user_obj.email and user_obj.user_profile.first_name and user_obj.user_profile.gender:
        percentage += 20

    if user_obj.user_type == 'Student':
        if user_obj.user_profile.college and user_obj.user_profile.course and user_obj.user_profile.year:
            percentage += 20
    elif user_obj.user_type == 'Professional':
        if user_obj.user_profile.company_name and user_obj.user_profile.designation and user_obj.user_profile.experience_in_years:
            percentage += 20

    personal_interest_count = UserInterests.objects.filter(
        interest__masterinterest_id__interest_type='Personal',
        user=user_obj).count()

    career_interest_count = UserInterests.objects.filter(
        interest__masterinterest_id__interest_type='Career',
        user=user_obj).count()

    if personal_interest_count >= 1:
        percentage += 20

    if career_interest_count >= 1:
        percentage += 20

    return percentage


def send_welcome_push_notification(user_profile_obj=None):
    template_obj = NotificationMaster.objects.filter(
        slug_name='welcome').first()

    message = template_to_fcm_message(template_obj=template_obj,
                                      dynamic_context={
                                          "name": user_profile_obj.first_name
                                      })
    # send push notification
    FCMNoticicationsClass.send_push_notification(
        notification_obj=template_obj,
        user=user_profile_obj.user,
        title=template_obj.title, body=message)


def send_milescoins_push_notification(user_profile_obj=None, coins=None,step=None):
    template_obj = NotificationMaster.objects.filter(
        slug_name='milescoins_earned').first()

    message = template_to_fcm_message(template_obj=template_obj,
                                      dynamic_context={
                                          "name": user_profile_obj.first_name,
                                          "milescoins": coins,
                                          "step": step
                                      })
    # send push notification
    FCMNoticicationsClass.send_push_notification(
        user=user_profile_obj.user,
        notification_obj=template_obj,
        title=template_obj.title, body=message)
