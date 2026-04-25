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
import plugin.build
from tools import *

config = configparser.ConfigParser()
config.read('config.ini')

ask_groups = json.loads(config.get('group-zone', 'ask'))
answer_groups = json.loads(config.get('group-zone', 'answer'))
total_groups = json.loads(config.get('group-zone', 'total'))

bot_ip = config.get('web', 'bot_ip')
global_ip = config.get('web', 'global_ip')
http_service_port = config.get('web', 'http_service_port')
http_website_port = config.get('web', 'http_website_port')

api_key = os.environ.get('DEEPSEEK_API_KEY')

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")


# 向回答群通知新提问
def notice_about_ask(qid, qtype, qtitle, content, group_id, user_id, is_first : bool = False):
    url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
    message = [
        {
            "type": "text",
            "data": {
                "text": f"已收到来自 {plugin.build.get_group_name(group_id)} {plugin.build.get_user_name(group_id, user_id)}"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f" 的新提问，编号为 #{qid}，归类为 {qtype}：\n" if is_first else f" 关于问题 #{qid}:{qtitle} 的追问：\n"
                    
            }
        }
    ]
    # 添加问题内容
    for question in content:
        if question['type'] == 'text':
            question['data']['text'] = question['data']['text'].strip() + '\n'
        if question['type'] in ['text', 'image']:
            message.append(question)
    message += [{
        "type": "text",
        "data": {
            "text": f"\n问题链接：http://{global_ip}:{http_website_port}/{qtype}.html#q{qid}\n如需回答，请使用 #{qid} 开头的消息."
        }
    }]
    for group_id in answer_groups:
        payload = {
            "group_id": group_id,
            "message": message
        }
        responce = requests.post(url=url, json=payload)
        
        if responce.status_code == 200:
            send_message_id = responce.json()['data']['message_id']
            store_question_id(qid, send_message_id)


# 向提问群通知新回答
def notice_about_answer(qid, qtype, qtitle, content, group_id):
    url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
    message = [
        {
            "type": "text",
            "data": {
                "text": f"已收到关于问题 #{qid}:{qtitle} 的回答：\n"
            }
        }
    ]
    # 添加问题内容
    for answer in content:
        if answer['type'] == 'text':
            answer['data']['text'] = answer['data']['text'].strip() + '\n'
        if answer['type'] in ['text', 'image']:
            message.append(answer)
    message += [{
        "type": "text",
        "data": {
            "text": f"\n问题链接：http://{global_ip}:{http_website_port}/{qtype}.html#q{qid}\n如需继续追问，请使用 #{qid} 开头的消息."
        }
    }]
    payload = {
        "group_id": group_id,
        "message": message
    }
    responce = requests.post(url=url, json=payload)
    
    if responce.status_code == 200:
        send_message_id = responce.json()['data']['message_id']
        store_question_id(qid, send_message_id)


# 获取问题的 message_id
def get_message_question_id(message_id) -> int:
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question_id FROM questionIds WHERE message_id = ?
    ''', (message_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return int(result[0])
    return None


# 存储一条 questionIds 记录
def store_question_id(question_id, message_id):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questionIds (question_id, message_id)
        VALUES (?, ?)
    ''', (question_id, message_id))
    conn.commit()
    conn.close()


# 检测到新增问题
def add_question(message_id, content, group_id, user_id, timestamp):
    # 检索 timestamp 时间节点前 1 分钟内的所有消息，然后全部拼接到 content 中，作为问题的完整内容
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    # 格式化 timestamp
    one_minute_ago = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp - 60))
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    cursor.execute('''
        SELECT message FROM messages
        WHERE group_id = ? AND user_id = ? AND timestamp >= ? AND timestamp <= ?
    ''', (group_id, user_id, one_minute_ago, formatted_time))
    content = []
    for row in cursor.fetchall():
        content += json.loads(row[0])
    content = delete_qqq(content)
    save_images(content)  # 保存图片到本地，并替换消息中的图片链接为本地链接
    # 检索最大的 question_id
    cursor.execute('SELECT MAX(question_id) FROM questions')
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    # 检查 user_id 是否为学生
    cursor.execute('SELECT user_type FROM users WHERE qq_id = ?', (user_id,))
    result = cursor.fetchone()
    user_type = result[0] if result else None

    if user_type != '学生':
        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": "[warning] 只有学生的提问才会被记录和通知."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)
        return  # 只有学生的提问才会被记录和通知
    
    # AI 判断问题的类别
    system_content = """
    接下来用户会给你提供一个高级语言程序设计课程群聊中的提问内容，你需要为提问内容归类，类别如下：
    
    document：这一类是对课程文档作业(网站)内容的相应提问，例如问文档作业网站为什么进不去，例如问某个题是否需要给出warning截图；
    programming：这一类是对课程编程作业内容的相应提问，例如和demo相关的问题，例如问txt_compare的结果为什么不一致；
    technology：这一类是对课程技术的相应提问，体现出了用户对课程某块知识点的思考（这类问题较少，如果你碰到了请勿错过）。

    #Q# 属于提问格式要求，无任何特殊含义。
    你的回复内容只能是一个单词，只能是document/programming/technology之一，单词小写，不要添加任何附加内容包括标点符号。
    """
    ocr_message = get_raw_message(content, ocr=True)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": ocr_message},
        ],
        stream=False
    )
    reply_type = response.choices[0].message.content

    if reply_type not in ['document', 'programming', 'technology']:
        reply_type = 'unknown'

    # AI 总结问题的标题
    system_content = """
    接下来用户会给你提供一个高级语言程序设计课程群聊中的提问内容，你需要为提问内容总结一个标题，要求如下：
    标题要求简短，不能超过10个字，且要能够体现问题的核心内容。
    你的回复内容只能是标题文本，不要添加任何附加内容包括标点符号。
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": ocr_message},
        ],
        stream=False
    )
    reply_title = response.choices[0].message.content
    # 插入新问题
    cursor.execute('''
        INSERT INTO questions (question_type, question_title, group_id, user_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (reply_type, reply_title, group_id, user_id, formatted_time))
    # 插入首次的问题记录
    cursor.execute('''
        INSERT INTO questionNotes (question_id, message_id, content, is_question, is_first, group_id, user_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (max_id + 1, message_id, json.dumps(content), True, True, group_id, user_id, formatted_time))
    conn.commit()
    conn.close()
    store_question_id(max_id + 1, message_id)

    plugin.build.website_rebuild() # 构建网页

    # 通知答疑群
    notice_about_ask(max_id + 1, reply_type, reply_title, content, group_id, user_id, is_first = True)

    url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
    payload = {
        "group_id": group_id,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": "已收到来自"
                }
            },
            {
                "type": "at",
                "data": {
                    "qq": user_id
                }
            },
            {
                "type": "text",
                "data": {
                    "text": f" 的新提问，编号为 #{max_id + 1}，归类为 {reply_type}，如需追问，请使"
                    f"用 #{max_id + 1} 开头的消息进行追问. 问题链接：http://{global_ip}:{http_website_port}/{reply_type}.html#q{max_id+1}"
                }
            }
        ]
    }
    responce = requests.post(url=url, json=payload)
    if responce.status_code == 200:
        send_message_id = responce.json()['data']['message_id']
        store_question_id(max_id + 1, send_message_id)


# 增加问题记录
def add_question_note(message_id, question_id, content, group_id, user_id, timestamp):
    content = delete_qn(content, question_id)
    save_images(content)  # 保存图片到本地，并替换消息中的图片链接为本地链接
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    # 获取 question_id
    cursor.execute('''
        SELECT question_type, question_title, group_id FROM questions
        WHERE question_id = ?
    ''', (question_id,))
    result = cursor.fetchone()
    if result is None:
        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": f"[warning] 问题编号 #{question_id} 不存在，无法添加记录."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)
        return  # 没有找到对应的问题，无法添加记录
    qtype, qtitle, from_group_id = result
    # 格式化 timestamp
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    # 获取 user_id 身份
    cursor.execute('SELECT user_type FROM users WHERE qq_id = ?', (user_id,))
    result = cursor.fetchone()
    user_type = result[0] if result else None
    is_question = True if user_type == '学生' else False  # 学生的消息视为问题，其他视为回答
    # 插入问题记录
    cursor.execute('''
        INSERT INTO questionNotes (question_id, message_id, content, is_question, is_first, group_id, user_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (question_id, message_id, json.dumps(content), is_question, False, group_id, user_id, formatted_time))
    conn.commit()
    conn.close()

    store_question_id(question_id, message_id)

    plugin.build.website_rebuild() # 构建网页，更新问题记录

    # 通知答疑群
    if is_question:
        notice_about_ask(question_id, qtype, qtitle, content, group_id, user_id)
        
        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": "已收到来自"
                    }
                },
                {
                    "type": "at",
                    "data": {
                        "qq": user_id
                    }            },
                {
                    "type": "text",
                    "data": {
                        "text": f" 的消息，已添加到 #{question_id} 的记录中."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)

    if not is_question and group_id in answer_groups:
        notice_about_answer(question_id, qtype, qtitle, content, from_group_id)


def move_to_open(question_id, group_id):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    # 计算时间字符串
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor.execute('''
        UPDATE questions SET is_open = 1, timestamp = ? WHERE question_id = ?
    ''', (formatted_time, question_id,))
    conn.commit()
    # 获取问题类型
    cursor.execute('''
        SELECT question_type FROM questions WHERE question_id = ?
    ''', (question_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        qtype = result[0]
        plugin.build.website_rebuild() # 构建网页，更新问题状态

        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": f"已成功将问题 Q{question_id} 设置为开放状态."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)


def move_to_close(question_id, group_id):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor.execute('''
        UPDATE questions SET is_open = 0, timestamp = ? WHERE question_id = ?
    ''', (formatted_time, question_id,))
    conn.commit()
    # 获取问题类型
    cursor.execute('''
        SELECT question_type FROM questions WHERE question_id = ?
    ''', (question_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        qtype = result[0]
        plugin.build.website_rebuild() # 构建网页，更新问题状态

        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": f"已成功将问题 #{question_id} 设置为关闭状态."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)


def move_to_typical(question_id, group_id):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor.execute('''
        UPDATE questions SET is_typical = 1, timestamp = ? WHERE question_id = ?
    ''', (formatted_time, question_id,))
    conn.commit()
    # 获取问题类型
    cursor.execute('''
        SELECT question_type FROM questions WHERE question_id = ?
    ''', (question_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        qtype = result[0]
        plugin.build.website_rebuild() # 构建网页，更新问题状态

        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": f"已成功将问题 #{question_id} 设置为典型问题."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)


def move_to_unmeaningful(question_id, group_id):
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor.execute('''
        UPDATE questions SET is_unmeaningful = 1, timestamp = ? WHERE question_id = ?
    ''', (formatted_time, question_id,))
    conn.commit()
    # 获取问题类型
    cursor.execute('''
        SELECT question_type FROM questions WHERE question_id = ?
    ''', (question_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        qtype = result[0]
        plugin.build.website_rebuild() # 构建网页，更新问题状态

        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": f"已成功将问题 #{question_id} 设置为无意义问题."
                    }
                }
            ]
        }
        requests.post(url=url, json=payload)


# 检查开放的问题，在回答群提醒
def check_open_questions():
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3600))
    cursor.execute('''
        SELECT question_id, question_type, question_title, group_id, user_id, timestamp
        FROM questions WHERE timestamp < ? AND is_open = 1
    ''', (formatted_time,))
    text = "所有超过 1 小时未解决的问题列表：\n\n"
    idx = 0
    for row in cursor.fetchall():
        question_id, question_type, question_title, group_id, user_id, timestamp = row
        idx += 1
        text += f"({idx}) 来自群{plugin.build.get_group_name(group_id)} 学生{plugin.build.get_user_name(group_id, user_id)} 的问题：#{question_id}:{question_title} " + \
        f"问题链接：http://{global_ip}:{http_website_port}/{question_type}.html#q{question_id}\n"
    conn.close()
    if idx > 0:
        url = f"http://{bot_ip}:{http_service_port}/send_group_msg"
        for group_id in answer_groups:
            payload = {
                "group_id": group_id,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": text
                        }
                    }
                ]
            }
            requests.post(url=url, json=payload)