import pytesseract
from PIL import Image, UnidentifiedImageError
import requests
import os
from datetime import datetime, timedelta
import re

# 设置Tesseract的路径（适用于GitHub Actions环境）
pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def get_last_day_of_previous_month(year, month):
    if month == 1:
        last_month = datetime(year - 1, 12, 1)
    else:
        last_month = datetime(year, month - 1, 1)
    last_day = last_month + timedelta(days=32)  # 确保移到下个月
    last_day = last_day.replace(day=1) - timedelta(days=1)
    return last_day

def get_image_url():
    today = datetime.now()
    last_day_of_prev_month = get_last_day_of_previous_month(today.year, today.month)
    date_str = last_day_of_prev_month.strftime("%Y/%m/%d")
    img_url = f'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/xyL/{last_day_of_prev_month.year}/qy/{date_str[-5:].replace("/", "")}pc.jpg'
    return img_url

def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as handler:
            handler.write(response.content)
    else:
        raise Exception(f"Failed to download image, status code: {response.status_code}")
def simplify_text_formatting(text):
    text = re.sub(r'\n+', '\n', text).strip()  # 移除多余的换行
    text = re.sub(r'\s+', ' ', text)  # 多余的空格替换为单个空格
    return text
def ocr_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
        text = simplify_text_formatting(text)
        return text
    except UnidentifiedImageError:
        raise Exception(f"Cannot identify image file '{image_path}'")

def send_wxpusher_message(message):
    app_token = os.getenv('APP_TOKEN')  # 从环境变量中读取AppToken
    uids = os.getenv('UIDS').split(',')  # 从环境变量中读取UID列表（多个UID用逗号分隔）
    url = 'https://wxpusher.zjiecode.com/api/send/message'
    data = {
        "appToken": app_token,
        "content": message,
        "contentType": 1,  # 1表示文本消息
        "uids": uids,
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

def job():
    try:
        print("Running job...")
        image_url = get_image_url()
        print(f"Image URL: {image_url}")
        download_image(image_url, 'image.jpg')
        print("Image downloaded successfully.")
        text = ocr_image('image.jpg')
        print("OCR completed.")
        # 输出OCR结果，便于调试
        print("OCR Result:", text)
        send_wxpusher_message(text)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        send_wxpusher_message(error_message)

job()
