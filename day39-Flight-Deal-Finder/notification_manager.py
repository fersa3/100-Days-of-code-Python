from os import environ
from dotenv import load_dotenv
from twilio.rest import Client

class NotificationManager:
    """
        This class is responsible for sending notifications with the deal flight details.
    """
    def __init__(self):
        load_dotenv()
        self._account_sid = environ.get("TWILIO_ACCOUNT_SID")
        self._auth_token = environ.get("TWILIO_AUTH_TOKEN")
        self._from_number = environ.get("TWILIO_VIRTUAL_NUMBER")
        self._to_number = environ.get("MY_NUMBER")
        self._messaging_service_sid = environ.get("TWILIO_MESSAGING_SERVICE_SID")
        self.client = Client(self._account_sid, self._auth_token)

    def send_sms_to_customer(self, text):
        message = self.client.messages.create(
            messaging_service_sid=self._messaging_service_sid,
            body=text,
            to=self._to_number
        )
        # print(message.body)
        print("Message sent! 😉")