import pytesseract
from PIL import Image
import requests
import os

def ocr_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
    return text

def send_wechat_message(message):
    send_key = os.getenv('SEND_KEY')
    title = "定期任务通知"
    desp = message
    url = f'https://sctapi.ftqq.com/{send_key}.send'
    data = {
        "title": title,
        "desp": desp
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

def job():
    try:
        print("Running job...")
        text = ocr_image('/mnt/data/0531pc.jpg')
        send_wechat_message(text)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        send_wechat_message(error_message)

job()
