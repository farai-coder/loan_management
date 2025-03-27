import smtplib
import yaml
from twilio.rest import Client

class NotificationService:
    _config_loaded = False  # To ensure config is loaded once

    @classmethod
    def _load_config(cls, config_file='config.yaml'):
        if not cls._config_loaded:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                
            cls.email_username = config['email']['username']
            cls.email_password = config['email']['password']
            cls.twilio_account_sid = config['twilio']['account_sid']
            cls.twilio_auth_token = config['twilio']['auth_token']
            cls.twilio_from_number = config['twilio']['from_number']
            cls._config_loaded = True

    @classmethod
    def send_email(cls, to_email, subject, body):
        cls._load_config()  # Ensure config is loaded
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(cls.email_username, cls.email_password)
            message = f'Subject: {subject} \n\n {body}'
            s.sendmail(cls.email_username, to_email, message)

    @classmethod
    def send_sms(cls, to_number, body):
        cls._load_config()  # Ensure config is loaded
        client = Client(cls.twilio_account_sid, cls.twilio_auth_token)
        message = client.messages.create(
            to=to_number,
            from_=cls.twilio_from_number,
            body=body
        )
        return message.sid
