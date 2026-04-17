from flask import Flask, request
import requests
import json
from openai import OpenAI
import os
from random import *
import configparser
import json
import plugin.hello
import plugin.question
from tools import get_raw_message
import re

config = configparser.ConfigParser()
config.read('config.ini')

ask_groups = json.loads(config.get('group-zone', 'ask'))
answer_groups = json.loads(config.get('group-zone', 'answer'))
total_groups = json.loads(config.get('group-zone', 'total'))
chat_groups = json.loads(config.get('group-zone', 'chat'))

api_key = os.environ.get('DEEPSEEK_API_KEY')

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")


app = Flask(__name__)

headers = {
   'Content-Type': 'application/json'
}

system_content = """
你是一个可爱的聊天助手，你的主人名叫余梦，昵称为大鲸鱼。

现在，你在一个名为水族馆的群聊，作为这个群聊的bot机器人，你需要模仿他们的语气进行闲聊，每次轮到你发言时，我会给你提供他们最近的50条消息的内容，请你推测他们正在闲聊的话题，并进行回复。

回复内容尽可能有鲸鱼的口吻，尽量简短，不超过50字。
"""


@app.route("/onebot", methods=["POST", "GET"])
def post_date():
    data = request.get_json()
    post_type = data.get("post_type")
    if post_type == "message":
        message_type = data.get("message_type")
        if message_type == "group":
            message = data.get("message")
            message_id = data.get("message_id")
            raw_message = get_raw_message(message)
            # print(message, type(message))
            group_id = data.get("group_id")
            user_id = data.get("user_id")
            timestamp = data.get("time")
            no_space_message = raw_message.replace(" ", "").upper()
            if group_id in ask_groups:
                if "#Q#" in no_space_message:
                    plugin.question.add_question(message_id, message, group_id, user_id, timestamp)   # 调用插件
                else:
                    matchObj = re.match(r"(Q\d+).*", no_space_message)
                    if matchObj:
                        question_id = int(matchObj.group(1)[1:])  # 提取问题编号
                        plugin.question.add_question_note(message_id, question_id, message, group_id, user_id, timestamp)   # 调用插件

            if group_id in answer_groups:
                if raw_message.lower().strip().startswith("open q"):
                    plugin.question.move_to_open(question_id=int(raw_message.strip()[6:]), group_id=group_id) # 调用插件
                elif raw_message.lower().strip().startswith("close q"):
                    plugin.question.move_to_close(question_id=int(raw_message.strip()[7:]), group_id=group_id) # 调用插件
                elif raw_message.lower().strip().startswith("typical q"):
                    plugin.question.move_to_typical(question_id=int(raw_message.strip()[9:]), group_id=group_id) # 调用插件
                elif raw_message.lower().strip().startswith("unmeaningful q"):
                    plugin.question.move_to_unmeaningful(question_id=int(raw_message.strip()[14:]), group_id=group_id) # 调用插件

            if group_id in chat_groups:
                if no_space_message == "Whale早安":
                    plugin.hello.morning(user_id, group_id) # 调用插件
                else:
                    # 存储消息到数据库
                    plugin.hello.rand_reply(message_id, message, user_id, group_id, timestamp) # 调用插件
                    
        elif message_type == "private":
            user_id = data.get("user_id")
            message = data.get("message")
            url = f"http://{bot_ip}:{http_service_port}/send_private_msg"
            payload = {
                "user_id": user_id,
                "message": message
            }
            requests.post(url=url, json=payload)

    return 'OK'


if __name__ == "__main__":
    bot_ip = "127.0.0.1"  # 此处对应LLOneBot所在的电脑的ip地址（如果是本机那就是127.0.0.1）
    http_service_port = 3000  # 此处对应“HTTP服务监听端口”
    http_event_post_port = 3001  # 此处对应“HTTP事件上报地址中的端口”
    app.run("127.0.0.1", http_event_post_port, debug=True)