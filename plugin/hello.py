from flask import Flask, request
import requests
import json
from openai import OpenAI
import os
from random import *
import configparser
import json
import time
import sqlite3
from tools import get_raw_message

config = configparser.ConfigParser()
config.read('config.ini')

ask_groups = json.loads(config.get('group-zone', 'ask'))
answer_groups = json.loads(config.get('group-zone', 'answer'))
total_groups = json.loads(config.get('group-zone', 'total'))

bot_ip = config.get('web', 'bot_ip')
http_service_port = config.get('web', 'http_service_port')

api_key = os.environ.get('DEEPSEEK_API_KEY')

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

system_content = """
你是一个可爱的聊天助手，你的主人名叫余梦，昵称为大鲸鱼。

现在，你在一个名为水族馆的群聊，作为这个群聊的bot机器人，你需要模仿他们的语气进行闲聊，每次轮到你发言时，我会给你提供他们最近的20条消息的内容，请你推测他们正在闲聊的话题，并进行回复。

回复内容尽可能有鲸鱼的口吻，尽量简短，不超过50字。
"""

def morning(user_id, group_id):
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"插件触发时间: {formatted_time}")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"用户于 {formatted_time} 起床，请你参考用户的起床时间。回复它的内容：早安"},
        ],
        stream=False
    )
    reply_content = response.choices[0].message.content
    print(reply_content)
    url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
    payload = {
        "group_id": group_id,
        "message": [
            {  
                "type": "at",
                "data": {
                    "qq": user_id,
                }
            },
            {
                "type": "text",
                "data": {
                    "text": " "+reply_content
                }
            }
        ]
    }
    requests.post(url=url, json=payload)


def store_message(message_id, message, group_id, user_id, timestamp):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    cursor.execute('''
        INSERT INTO messages (message_id, group_id, user_id, timestamp, message) VALUES (?, ?, ?, ?, ?)
    ''', (message_id, group_id, user_id, formatted_time, json.dumps(message)))
    conn.commit()
    conn.close()


def rand_reply(message_id, message, user_id, group_id, timestamp):
    # 获取该群最近50条消息
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message FROM messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT 50
    ''', (group_id,))
    message_list = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    # 1% 概率触发消息回复
    k = randint(0,100-1)
    if k == 0 and len(message_list) >= 50:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": "\n".join([f"({idx}): {get_raw_message(_)}" for idx, _ in enumerate(message_list[-50:])])},
            ],
            stream=False
        )
        reply_content = response.choices[0].message.content
        print(reply_content)
        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": reply_content
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)