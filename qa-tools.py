from tools import *
import configparser
import requests
import os
import json
import base64

config = configparser.ConfigParser()
config.read('config.ini')

bot_ip = config.get('bot', 'ip')
global_ip = config.get('bot', 'global_ip')
http_service_port = config.get('bot', 'http_service_port')
image_save_path = config.get('path', 'image_save_path')

image = f'{image_save_path}/65CAF9470B81728E186D714AEAF77649.png'


def get_baidu_access_token():
    client_id = os.getenv('BAIDU_OCR_API_KEY')
    client_secret = os.getenv('BAIDU_OCR_SECRET_KEY')
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"

    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    access_token = response.json()["access_token"]
    return access_token


def ocr_image(image_path) -> str:
    access_token = get_baidu_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
    
    with open(image_path, 'rb') as f:
        img_data = f.read()
    
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    payload = {
        'image': img_base64
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        result = response.json()
        if 'words_result' in result:
            text = '\n'.join([item['words'] for item in result['words_result']])
            return text
        else:
            return "No text found in the image."
    else:
        return f"Error: {response.status_code} - {response.text}"


if __name__ == "__main__":
    text = ocr_image(image)
    print(text)
