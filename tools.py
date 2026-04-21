import re
import configparser
import requests
import os
import sqlite3

config = configparser.ConfigParser()
config.read('config.ini')

bot_ip = config.get('web', 'bot_ip')
global_ip = config.get('web', 'global_ip')

http_service_port = config.get('web', 'http_service_port')
http_website_port = config.get('web', 'http_website_port')

image_save_path = config.get('path', 'image_save_path')


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


def ocr_image(image_url) -> str:
    access_token = get_baidu_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
    
    payload = {
        'url': image_url
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


def get_raw_message(message : list, ocr : bool = False) -> str:
    raw_message = ""
    for item in message:
        if item["type"] == "text":
            raw_message += item["data"]["text"] + '\n\n'
        elif item["type"] == "at":
            # raw_message += f"@{item['data']['qq']} " + '\n\n'
            raw_message += ""
        elif item["type"] == "image":
            # 先进行图片的 ocr 识别
            if ocr:
                ocr_result = ocr_image(item['data']['url'])
                raw_message += "[图片<ocr>" + ocr_result + "</ocr>] "
            else:
                raw_message += f"![图片]({image_save_path}/{item['data']['file']}) \n\n"  # 替换为本地图片链接
        elif item["type"] == "face":
            raw_message += f"[表情{item['data']['id']}] \n"
        # 可以根据需要添加更多类型的处理
    return raw_message.strip()


# 获取所有的文本消息
def get_text_message(message : list) -> str:
    text_message = ""
    for item in message:
        if item["type"] == "text":
            text_message += item["data"]["text"]

    text_message = text_message.strip()
    return text_message


# 删除消息中的 #Q# 提问标记
def delete_qqq(message : list) -> list:
    new_message = []
    for item in message:
        if item["type"] == "text":
            status = 0  # status 为 1 对应 #，2 对应 #Q，3 对应 #Q#（表示找到）
            qqq_begin_idx, qqq_end_idx = -1, -1
            for idx, ch in enumerate(item["data"]["text"]):
                if ch == " " or ch == "\t" or ch == "\n":
                    continue
                if status == 1 and ch != 'Q' or status == 2 and ch != '#':
                    status = 0  # reset 状态机
                if status == 0 and ch == "#":
                    status = 1
                    qqq_begin_idx = idx
                elif status == 1 and ch == "Q":
                    status = 2
                elif status == 2 and ch == "#":
                    status = 3
                    qqq_end_idx = idx
                    break

            # 检测 qqq_begin_idx 和 status 来判断是否找到 #Q#，如果找到则删除
            if status == 3:
                item["data"]["text"] = item["data"]["text"][:qqq_begin_idx] + item["data"]["text"][qqq_end_idx+1:]

        new_message.append(item)

    return new_message


# 删去 Q{} 追问标记
def delete_qn(message : list, number : int) -> list:
    new_message = []
    for item in message:
        if item["type"] == "text":
            item["data"]["text"] = re.sub(rf"#\s*{number}", "", item["data"]["text"])

        new_message.append(item)

    return new_message


def save_images(message : list):
    for item in message:
        if item["type"] == "image":
            image_url = item['data']['url']
            # 下载图片并保存到本地
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = response.content
                # 生成唯一的文件名，可以使用时间戳或 UUID
                filename = f"./website/pics/{item['data']['file']}"
                with open(filename, 'wb') as f:
                    f.write(image_data)
