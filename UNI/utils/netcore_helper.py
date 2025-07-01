import logging
from django.template import Template, Context
import pytz
import requests
import json
from datetime import datetime
import utils
from django.conf import settings
from apps.notifications.utils import send_templated_email_via_mandrill, get_email_template


# from apps.jobs.models import ApplicationMeeting


class NotificationProxy:
    API_URL = "https://api2.netcoresmartech.com/v1/activity/upload"
    AUTHORIZATION_HEADER = "Bearer 9fe318e8ece9299a6945bea578bad979"  # Example token, store securely

    def __init__(self, notification_object):
        """
        Initialize with a notification object that contains all necessary data.
        """
        self.notification_object = notification_object

    def get_asset_id(self):
        # Retrieve asset_id from the passed object or use the default
        # return self.notification_object.get("asset_id", "5110a91370e379b21165d47435cf6106")
        return "5110a91370e379b21165d47435cf6106"

    def get_activity_name(self):
        # Retrieve activity_name from the passed object or use the default
        # return self.notification_object.get("activity_name", "TEST_HEALTHCARE_RECRUIT_LEVEL")
        return "TEST_HEALTHCARE_RECRUIT_LEVEL"

    def get_activity_params(self):
        # Retrieve activity_params from the passed object or use default params
        candidate = self.notification_object.get('candidate_object')
        application_status_object = self.notification_object.get('application_status_object')
        pipeline_object = self.notification_object.get('pipeline_object')
        application_meeting = self.notification_object.get('application_meeting')
        interview_time = 'interview_time'
        if application_meeting:
            recruiter_name = application_meeting.recruiter.first_name
            interview_date = application_meeting.interview_date
        else:
            recruiter_name = "Test"  # candidate.app_owner.first_name
            current_time = datetime.now().date()
            time = current_time.strftime('%H:%M')
            # formatted_time = current_time.isoformat()
            interview_date = f'{current_time}'  # "2024-10-12T13:30:48.269821+00:00"
            interview_time = f'{time}'

        return self.notification_object.get("activity_params", {
            "level": f"{application_status_object.pipeline_status.netcore_status} | {pipeline_object.netcore_activity_name}",
            "first_name": candidate.first_name,
            "phone": candidate.mobile,
            "email": candidate.email,
            "recruiter_name": recruiter_name,  # we need to bring recruiter obj from L2
            "interview_date": interview_date,  # application_status_object
            "interview_time": interview_time,
            "linkedin_profile": "kkk@m.com",
            # "candidate_slug": self.get_slug_name()
        })

    def get_slug_name(self):
        # Retrieve slug_name from the passed object or use default slug
        # return self.notification_object.get("slug_name", "117262314271230066139GKe")
        return "117262314271230066139GKe"

    def get_recruiter(self):
        pass

    def send_notification(self):
        # Build the payload using the provided object
        asset_id = self.get_asset_id()
        activity_name = self.get_activity_name()
        activity_params = self.get_activity_params()

        notification_data = [{
            "asset_id": asset_id,
            "activity_name": activity_name,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
            "identity": "91c2c790-3fab-44b8-96f2-8ccc8f228433",
            # str(uuid.uuid4()),  # Example UUID for identity, replace with the actual value
            "activity_source": "web",
            "activity_params": activity_params
        }]

        headers = {
            "Authorization": self.AUTHORIZATION_HEADER,
            "Content-Type": "application/json"
        }

        # Send the POST request to the third-party API
        try:
            response = requests.post(self.API_URL, headers=headers, data=json.dumps(notification_data))
            if response.status_code == 200:
                print("Notification sent successfully!")
                test = response.json()
                logging.info(f"Netcore trigger response: {response.content}, response json: {response.json()}")
                return response.json()
            else:
                print(f"Error sending notification. Status code: {response.status_code}")
                logging.error(f"Error Netcore trigger Status code: {response.status_code}")
                return response.json()
        except Exception as e:
            print(f"Exception occurred: {e}")
            return {"error": str(e)}

    def send_email_notification(self, is_custom=False, cc_emails=None):
        # Build the payload using the provided object
        candidate = self.notification_object.get('candidate_object')
        application_status_object = self.notification_object.get('application_status_object')
        pipeline_object = self.notification_object.get('pipeline_object')
        candidate_application = self.notification_object.get('candidate_application')
        application_meeting = self.notification_object.get('meeting_object')
        previous_pipeline_status = self.notification_object.get('previous_pipeline_status')
        current_pipeline_status = self.notification_object.get('current_pipeline_status')
        is_created = self.notification_object.get('is_created')
        custom_template = self.notification_object.get('custom_template', None)

        recruiter_first_name, recruiter_email, spoc_email, interview_date, interview_time, recruiter_linkedin, spoc_mobile, spoc_first_name, spoc_linkedin, offer_link, email_subject, rendered_html = "", "", "", "", "", "https://www.linkedin.com/", "", "", "https://www.linkedin.com/", None, None, None

        utils.constants.trigger_event_notification(candidate.app_owner, 'Status Change',
                                   f'{candidate.first_name}',
                                   "Miles Recruit - Status Change",
                                   device_type='Web')
        if hasattr(candidate, 'app_owner') and candidate.app_owner:
            spoc_first_name = candidate.app_owner.first_name
            spoc_email = candidate.app_owner.email
            spoc_mobile = candidate.app_owner.mobile
            spoc_linkedin = candidate.app_owner.linkedin_url

        if str(current_pipeline_status.netcore_status).lower() == 'loi_offer_released' and candidate_application:
            offer_link = f'{settings.FED_BASE_URL}/offerLater?application_id={candidate_application.id}&token={candidate.unique_id}'
            candidate_application.offer_released_time = datetime.now()
            candidate_application.save()

        if application_meeting:
            recruiter_first_name = application_meeting.recruiter.first_name
            interview_date = f'{application_meeting.start_time.date()}'
            interview_time = application_meeting.start_time

            ist_tz = pytz.timezone('Asia/Kolkata')
            start_time_ist = interview_time.astimezone(ist_tz)
            interview_time = start_time_ist.strftime('%I:%M %p')

            recruiter_linkedin = application_meeting.recruiter.linkedin_url  # linkedin_url
        if hasattr(application_meeting, 'recruiter'):
            if application_meeting.recruiter:
                recruiter_email = application_meeting.recruiter.email
        message = None
        if is_custom and custom_template.slug:
            if custom_template.slug == "loi_issued":
                template, context, email_subject = get_email_template(custom_template.slug)
                custom_context = {"candidate_name": candidate.first_name, 'candidate_phone': candidate.mobile,
                                  'candidate_email': candidate.email, 'recruiter_name': recruiter_first_name,
                                  'recruiter_email': recruiter_email, 'interview_date': interview_date,
                                  'interview_time': interview_time, 'recruiter_linkedin': recruiter_linkedin,
                                  'offer_link': candidate_application.offer_link.url, "interviewer_name": recruiter_first_name,
                                  'spoc_email': spoc_email, 'spoc_mobile': spoc_mobile,
                                  'spoc_linkedin_url': spoc_linkedin, 'spoc_first_name': spoc_first_name}
                merge_context = {**context, **custom_context}
                rendered_html = template.render(Context(merge_context))
            else:
                template, context, email_subject = get_email_template(custom_template.slug)
                custom_context = {"candidate_name": candidate.first_name, 'candidate_phone': candidate.mobile,
                                  'candidate_email': candidate.email, 'recruiter_name': recruiter_first_name,
                                  'recruiter_email': recruiter_email, 'interview_date': interview_date,
                                  'interview_time': interview_time, 'recruiter_linkedin': recruiter_linkedin,
                                  'offer_link': offer_link, "interviewer_name": recruiter_first_name,
                                  'spoc_email': spoc_email, 'spoc_mobile': spoc_mobile,
                                  'spoc_linkedin_url': spoc_linkedin, 'spoc_first_name': spoc_first_name}
                merge_context = {**context, **custom_context}
                rendered_html = template.render(Context(merge_context))
        else:
            if str(current_pipeline_status.netcore_status).lower() == 'l1_assigned':
                template, context, email_subject = get_email_template('l1_welcome_email')
                custom_context = {"candidate_name": candidate.first_name, 'recruiter_name': recruiter_first_name,
                                  'recruiter_email': recruiter_email}
                merge_context = {**context, **custom_context}
                rendered_html = template.render(Context(merge_context))
                # send_templated_email_via_mandrill(subject=email_subject, body=None, html_content=rendered_html,
                #                                   to_emails=[candidate.email, spoc_email],
                #                                   from_email="stem.nursing@milestalenthub.com", from_name="Healthcare")
            else:
                if current_pipeline_status.netcore_status and current_pipeline_status.netcore_status not in ['false',
                                                                                                             'False']:
                    if current_pipeline_status.netcore_status == "loi_offer_released":
                        candidate_application.offer_released_time = datetime.now()
                        candidate_application.save()
                    template, context, email_subject = get_email_template(current_pipeline_status.netcore_status)
                    custom_context = {"candidate_name": candidate.first_name, 'candidate_phone': candidate.mobile,
                                      'candidate_email': candidate.email, 'recruiter_name': recruiter_first_name,
                                      'recruiter_email': recruiter_email, 'interview_date': interview_date,
                                      'interview_time': interview_time, 'recruiter_linkedin': recruiter_linkedin,
                                      'offer_link': offer_link, "interviewer_name": recruiter_first_name,
                                      'spoc_email': spoc_email, 'spoc_mobile': spoc_mobile,
                                      'spoc_linkedin_url': spoc_linkedin, 'spoc_first_name': spoc_first_name}
                    merge_context = {**context, **custom_context}
                    rendered_html = template.render(Context(merge_context))
                    # print(rendered_html)
        if rendered_html:
            send_templated_email_via_mandrill(subject=email_subject, body=None, html_content=rendered_html,
                                              to_emails=[candidate.email, spoc_email],
                                              from_email="stem.nursing@milestalenthub.com", from_name="Healthcare", cc_emails=cc_emails)
