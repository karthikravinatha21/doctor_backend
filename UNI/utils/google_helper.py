import os
import json
import uuid

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
from django.conf import settings
# from google.auth.credentials import Credentials
from google.oauth2.credentials import Credentials

from apps.contacts.models import ContactAvailabilitySlot
from utils.constants import convert_to_iso_string


class GoogleCalendarManager:
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive.file', ]
    CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                      'client_secret_154625965269-pvgpnqc7ljba0rkfuh1ssj9v1jm1c98u.apps.googleusercontent.com.json')
    ACCESS_TOKEN = os.path.join(settings.BASE_DIR, 'token.json')  # Change to JSON file

    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        # Check if the token file exists and load credentials from it
        if os.path.exists(self.ACCESS_TOKEN):
            try:
                with open(self.ACCESS_TOKEN, 'r') as token:
                    credentials_data = token.read()
                    if credentials_data:  # Check if the file is empty
                        creds_data = json.loads(credentials_data)
                        # crediential = self.load_credentials_from_json(creds_data)
                        crediential = Credentials.from_authorized_user_file(self.ACCESS_TOKEN, self.SCOPES)
                        self.creds = crediential
                    else:
                        print("Token file is empty.")
            except json.JSONDecodeError as e:
                print(f"Error loading token file: {e}. File might be corrupted.")
            except Exception as e:
                print(f"Unexpected error: {e}")

        # If no valid credentials exist or credentials are expired, refresh or request new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE, self.SCOPES,
                    redirect_uri="http://localhost:8000/accounts/google/login/callback/")
                self.creds = flow.run_local_server(port=8080)
                print(self.creds.refresh_token)
                with open('token.json', "w") as token_file:
                    token_file.write(self.creds.to_json())

            # Save credentials to JSON file
            # self.save_credentials_to_json(self.creds)

        # Build the service object for interacting with the Google Calendar API
        self.service = build('calendar', 'v3', credentials=self.creds)

    def save_credentials_to_json(self, creds):
        """Convert credentials to a JSON-serializable format."""
        try:
            credentials_dict = self.save_credentials_to_json_helper(creds)
            with open(self.ACCESS_TOKEN, 'w') as token:
                json.dump(credentials_dict, token)
        except Exception as e:
            print(f"Error saving credentials to JSON: {e}")

    def save_credentials_to_json_helper(self, creds):
        """Helper function to convert credentials to a serializable format."""
        expiry_time = datetime.now() + timedelta(days=100)
        expiry_time_str = expiry_time.isoformat() if isinstance(expiry_time, datetime) else expiry_time
        return {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'expiry': expiry_time_str
        }

    def load_credentials_from_json(self, data):
        """Convert a JSON-serializable format back into a Credentials object."""
        try:
            creds = Credentials(
                token=data['token'],
                refresh_token=data['refresh_token'],
                token_uri=data['token_uri'],
                client_id=data['client_id'],
                client_secret=data['client_secret'],
                scopes=data['scopes']
            )
            # Set the expiry if available
            if data.get('expiry'):
                creds.expiry = datetime.fromisoformat(data['expiry'])
            return creds
        except KeyError as e:
            print(f"Missing key in the token data: {e}")
        except Exception as e:
            print(f"Error loading credentials from JSON: {e}")
        return None

    def refresh_token(self, creds):
        """ Refresh the access token using the refresh token. """
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # After refreshing, store the updated credentials (including new access token)
            self.save_credentials_to_json(creds)

        return creds

    def schedule_google_meeting(self, summary, start_time, end_time, description='', location='', attendees=None,
                                spoc_email=None):
        """Schedules a meeting using the Google Calendar API."""
        try:
            event = {
                'summary': summary,
                'location': location if location != "Google Hangouts" else "",
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [{'email': email} for email in attendees],
                'organizer': {
                    'email': spoc_email,
                },
                # 'reminders': {
                #     'useDefault': True,
                # },
                "reminders": {
                    "useDefault": False,  # Disable default reminders
                    "overrides": [
                        {"method": "email", "minutes": 1440},  # Email reminder 1 day before (1440 minutes)
                        {"method": "popup", "minutes": 1440},  # Popup notification 1 day before
                        {"method": "email", "minutes": 60},  # Email reminder 30 minutes before
                        {"method": "popup", "minutes": 60}  # Popup notification 30 minutes before
                    ]
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"{uuid.uuid4()}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet',  # For Google Meet
                        },
                        'status': {
                            'statusCode': 'success',
                        },
                    },
                },
            }

            # Create the event using the Google Calendar API
            # event_result = self.service.events().insert(
            #     calendarId='primary',
            #     body=event,
            #     sendUpdates='all').execute()
            event_result = self.service.events().insert(calendarId='primary',
                                                        body=event,
                                                        sendUpdates='all',
                                                        conferenceDataVersion=1).execute()

            print(f"Event created: {event_result['summary']} at {event_result['start']['dateTime']}")
            return event_result
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def cancel_meeting(self, event_id):
        """Cancels a scheduled meeting."""
        try:
            # cancel_object = self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            # print(f"Meeting with ID {event_id} was canceled successfully.")
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            event['status'] = 'cancelled'  # Mark event as cancelled

            cancel_object = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'  # Sends cancellation email to all attendees
            ).execute()
            return cancel_object
        except Exception as error:
            print(f"An error occurred while canceling the meeting: {error}")

    def reschedule_meeting(self, event_id, new_start_time, new_end_time):
        """Reschedules an existing meeting."""
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

            event['start']['dateTime'] = convert_to_iso_string(new_start_time)
            event['end']['dateTime'] = convert_to_iso_string(new_end_time)

            # Update the event with new times
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            print(f"Meeting with ID {event_id} was rescheduled to {updated_event['start']['dateTime']}.")
            return updated_event
        except Exception as error:
            print(f"An error occurred while rescheduling the meeting: {error}")
            return None

    def fetch_meetings(self, start_date, end_date):
        """Fetches meetings scheduled within the given date range."""
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                print("No meetings found within the given date range.")
                return []

            print("Upcoming meetings:")
            for event in events:
                print(f"{event['summary']} ({event['start']['dateTime']})")
            return events

        except Exception as error:
            print(f"An error occurred while fetching meetings: {error}")
            return []

    def fetch_busy_meetings(self, recruiter_email, start_time, end_time):
        try:
            today = datetime.today().date()  # Use today's date for slot generation
            start_time = datetime.combine(today, datetime.strptime(start_time, "%H:%M").time())
            end_time = datetime.combine(today, datetime.strptime(end_time, "%H:%M").time())
            try:
                events_result = self.service.events().list(
                    calendarId=recruiter_email,
                    timeMin=start_time.isoformat() + "Z",
                    timeMax=end_time.isoformat() + "Z",
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
            except:
                events_result = {}

            events = events_result.get("items", [])
            busy_slots = []

            for event in events:
                from dateutil.parser import isoparse
                # event_start = datetime.fromisoformat(event["start"]["dateTime"][:-1])  # Remove 'Z' from datetime string
                # event_end = datetime.fromisoformat(event["end"]["dateTime"][:-1])
                # busy_slots.append((event_start, event_end))
                event_start = isoparse(event["start"]["dateTime"]).replace(tzinfo=None)
                event_end = isoparse(event["end"]["dateTime"]).replace(tzinfo=None)
                busy_slots.append((event_start, event_end))

            return busy_slots
        except Exception as ex:
            raise ex

    def get_available_calendar(self, shared_email, from_date, to_date):
        """Fetch events from a shared calendar (other person's calendar)."""
        start_time_local = datetime.combine(from_date, datetime.min.time())  # 00:00:00
        end_time_local = start_time_local + timedelta(days=1) - timedelta(seconds=1)  # 23:59:59

        # Define the timezone you're working with (e.g., Asia/Kolkata)
        local_tz = pytz.timezone('Asia/Kolkata')

        # Localize the datetime objects to the specified timezone
        start_time_local = local_tz.localize(start_time_local)
        end_time_local = local_tz.localize(end_time_local)

        # Convert local times to UTC
        start_time_utc = start_time_local.astimezone(pytz.UTC)
        end_time_utc = end_time_local.astimezone(pytz.UTC)

        # Convert to ISO format, as required by the Google Calendar API
        timeMin = start_time_utc.isoformat()
        timeMax = end_time_utc.isoformat()

        # Fetch events for the given day from the calendar
        try:
            events_result = self.service.events().list(
                calendarId=shared_email,
                timeMin=timeMin,
                timeMax=timeMax,
                maxResults=10,  # Limit the number of events (optional)
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        except:
            events_result = {}
        events = events_result.get('items', [])

        response = []
        event_dict = {}
        if not events:
            print('No upcoming events found.')

        def format_time(date_str):
            """Convert datetime string to hour:minute format (HH:MM)."""
            dt = datetime.fromisoformat(date_str.replace('Z', ''))
            return dt.strftime('%I:%M')

        for event in events:
            # Extract the start and end times
            start_time = event['start']['dateTime']
            end_time = event['end']['dateTime']

            # Format the start and end times to HH:MM format
            start_time_formatted = format_time(start_time)
            end_time_formatted = format_time(end_time)

            # Extract the date (YYYY-MM-DD)
            event_date = start_time[:10]

            # Create a list for that date if it doesn't exist
            if event_date not in event_dict:
                event_dict[event_date] = []

            # Add the event's start and end times
            event_dict[event_date].append({
                'start_time': start_time_formatted,
                'end_time': end_time_formatted
            })

        # for date, event_list in event_dict.items():
        #     print(f'"{date}": [')
        #     for event in event_list:
        #         print(f'    {{ "start_time": "{event["start_time"]}", "end_time": "{event["end_time"]}" }},')
        #     print('],')
        return event_dict

    def get_google_blocked_slots(self, recruiter_email, start_date, end_date):
        """ Fetch blocked slots from Google Calendar """
        try:
            events_result = self.service.events().list(
                calendarId=recruiter_email,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            blocked_slots = {}
            for event in events:
                slot_date = event['start']['dateTime'].split("T")[0]
                if slot_date not in blocked_slots:
                    blocked_slots[slot_date] = []
                blocked_slots[slot_date].append({
                    "start_time": event['start']['dateTime'].split("T")[1][:5],
                    "end_time": event['end']['dateTime'].split("T")[1][:5],
                    "meeting_details": {
                        "title": event.get("summary", "No Title"),
                        "agenda": event.get("description", "No Agenda"),
                        "attendees": [attendee["email"] for attendee in
                                      event.get("attendees", [])] if "attendees" in event else []
                    }
                })
            return blocked_slots

        except Exception as e:
            return []

    def check_google_calendar_conflict(self, working_hours, slot_date, start_time=None, end_time=None):
        """
        Check if the slot exists in Google Calendar before allowing updates or deletion.
        """
        try:
            slot_date = slot_date

            time_min = f"{slot_date}T00:00:00Z"
            time_max = f"{slot_date}T23:59:59Z"

            # Fetch Google Calendar events for this day
            events_result = self.service.events().list(
                calendarId="karthik.ravinatha@mileseducation.com", #recruiter_email,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            blocked_intervals = []

            for event in events:
                event_start = datetime.strptime(event['start']['dateTime'], "%Y-%m-%dT%H:%M:%S%z").time()
                event_end = datetime.strptime(event['end']['dateTime'], "%Y-%m-%dT%H:%M:%S%z").time()
                blocked_intervals.append((event_start, event_end))


            if not working_hours:
                return True

            work_start = working_hours.start_time
            work_end = working_hours.end_time

            # **Check if every part of working hours is blocked**
            current_time = work_start
            fully_blocked = True  # Assume all is blocked unless proven otherwise

            while current_time < work_end:
                # Check if the current time falls inside ANY blocked interval
                is_blocked = any(bs <= current_time < be for bs, be in blocked_intervals)

                if not is_blocked:
                    fully_blocked = False  # Found a free slot, so don't restrict modification
                    break  # No need to check further

                current_time = (datetime.combine(datetime.today(), current_time) + timedelta(
                    minutes=15)).time()  # Move in 15-min increments

            return fully_blocked  # If fully blocked, return True (Restrict updates/deletions)

        except Exception as e:
            print(f"Error checking Google Calendar: {e}")
            return False  # Assume no conflict if API fails
