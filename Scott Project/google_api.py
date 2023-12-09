
import openai
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play
import creds

#Google Calendar Imports
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import calendar
import dateutil.parser
from dateutil.relativedelta import relativedelta, MO


# OpenAI and Google Cloud API setup
openai.api_key = creds.open_ai_key  # Consider moving this to an environment variable for security reasons
client = texttospeech.TextToSpeechClient.from_service_account_file('key.json')

def text_to_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content

def openai_response(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=100,
        temperature=0.5
    )
    return response.choices[0].text.strip()

def process_prompt(prompt):
    """
    Processes the given prompt: sends it to OpenAI and returns the response text and audio content.
    """
    response_text = openai_response(prompt)  # Get response from OpenAI
    audio_content = text_to_speech(response_text)  # Convert response text to speech
    return response_text, audio_content



def google_calendar_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('key.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service


#Google Calendar
def add_event_to_calendar(service, command):
    # Parsing the command to extract event details
    parts = command.lower().split(" ")
    try:
        # Assuming the format "Add [event] to my calendar on [Day] at [Time]"
        event_name = parts[1]
        day_of_week = parts[6]
        event_time = parts[8]

        # Find the next date for the given day of week
        today = datetime.datetime.now()
        day_index = list(calendar.day_name).index(day_of_week.capitalize())
        next_day = today + relativedelta(weekday=MO(day_index))

        # Combine date and time
        event_start = datetime.datetime.combine(next_day.date(), dateutil.parser.parse(event_time).time())
        event_end = event_start + datetime.timedelta(hours=1)  # Assuming 1 hour duration

        # Create Google Calendar event
        event = {
            'summary': event_name.capitalize(),
            'start': {
                'dateTime': event_start.isoformat(),
                'timeZone': 'America/New_York',  # Change this to your timezone
            },
            'end': {
                'dateTime': event_end.isoformat(),
                'timeZone': 'America/New_York',  # Change this to your timezone
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"

    except Exception as e:
        return f"An error occurred: {str(e)}"


