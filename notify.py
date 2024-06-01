import pytesseract
from PIL import Image
import requests
import os

def get_last_day_of_month(year, month):
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    return last_day

def get_image_url():
    today = datetime.now()
    last_day_of_month = get_last_day_of_month(today.year, today.month)
    date_str = last_day_of_month.strftime("%Y/%m/%d")
    img_url = f'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/xyL/{today.year}/qy/{date_str[-5:].replace("/", "")}pc.jpg'
    return img_url

def download_image(url, path):
    img_data = requests.get(url).content
    with open(path, 'wb') as handler:
        handler.write(img_data)

def ocr_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
    return text

def send_wechat_message(message):
    send_key = os.getenv('SEND_KEY')
    title = "关于星越L的最新政策"
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
        image_url = get_image_url()
        download_image(image_url, 'image.jpg')
        text = ocr_image('image.jpg')
        send_wechat_message(text)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        send_wechat_message(error_message)

job()
