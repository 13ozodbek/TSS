from django.utils import timezone
import random
import datetime
import requests

BOT_ID = "6725176067:AAFYwaMgrBHuvq8V-iwzLOLNRjIVH1UYIBU"
CHAT_ID = '-1001853506087'   #"584066666"#Ozodbekniki    #2081729348 guruhniki
TELEGRAMBOT_URL = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"


def send_otp_code(otp_obj):
    formatted_time = otp_obj.otp_created.strftime('%m-%d-%h-%I:%M:%S')
    message = (f"Project: TTS-Authentication\n Username: {otp_obj.otp_user}\n "
               f"OTP: {otp_obj.otp_code}\n Key: \n "
               "sender: Administrator\n"
               f"Sent time: {formatted_time}")
    response = requests.get(TELEGRAMBOT_URL.format(BOT_ID, message, CHAT_ID))
    return response


def generate_random_number():
    return random.randint(1000, 9999)


def check_otp_expire(otp_obj):
    code_sent_time = otp_obj.otp_created
    allowed_time = datetime.timedelta(seconds=60) + code_sent_time
    if timezone.now() <= allowed_time:
        return True

