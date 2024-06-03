import pytesseract
from PIL import Image, UnidentifiedImageError
import requests
import os
from datetime import datetime, timedelta
import re
import time

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

def get_image_urls():
    today = datetime.now()
    last_day_of_prev_month = get_last_day_of_previous_month(today.year, today.month)
    date_str = last_day_of_prev_month.strftime("%Y/%m/%d")
    date_suffix = f'{last_day_of_prev_month.year}/qy/{date_str[-5:].replace("/", "")}pc.jpg'
    
    # 多个前缀列表
    prefixes = [
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/xyL/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/bycool/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/XyLZQ/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/HYpro/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/haoyueL/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/boyuecool/',
        'https://dm30webimages.geely.com/GeelyPromotion/ANEW2/binruiCOOL/',
        # 添加更多前缀
    ]
    
    img_urls = [f'{prefix}{date_suffix}' for prefix in prefixes]
    return img_urls

def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as handler:
            handler.write(response.content)
        return True
    else:
        print(f"Failed to download image from {url}, status code: {response.status_code}")
        return False

def simplify_text_formatting(text):
    # 清理多余的空行和空格
    text = re.sub(r'\n\s*\n', '\n', text.strip())
    text = re.sub(r'\s+', ' ', text)
    return text

def ocr_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
        text = simplify_text_formatting(text)
        return text
    except UnidentifiedImageError:
        raise Exception(f"Cannot identify image file '{image_path}'")

def send_wxpusher_message(message):
    app_token = os.getenv('APP_TOKEN')
    uids = os.getenv('UIDS').split(',')
    url = 'https://wxpusher.zjiecode.com/api/send/message'
    data = {
        "appToken": app_token,
        "content": message,
        "contentType": 1,
        "uids": uids,
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

def job():
    try:
        print("Running job...")
        image_urls = get_image_urls()
        image_path = 'image.jpg'
        for image_url in image_urls:
            print(f"Trying to download image from URL: {image_url}")
            if download_image(image_url, image_path):
                print("Image downloaded successfully.")
                try:
                    text = ocr_image(image_path)
                    print("OCR completed.")
                    print("OCR Result:", text)
                    send_wxpusher_message(text)
                except Exception as e:
                    error_message = f"An error occurred during OCR: {str(e)}"
                    print(error_message)
                    send_wxpusher_message(error_message)
            else:
                error_message = f"Failed to download image from URL: {image_url}"
                print(error_message)
                send_wxpusher_message(error_message)
            
            # 每条消息发送后等待1分钟
            time.sleep(60)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        send_wxpusher_message(error_message)

job()
