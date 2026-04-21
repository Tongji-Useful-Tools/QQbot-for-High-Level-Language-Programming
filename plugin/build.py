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
import subprocess
from tools import get_raw_message

config = configparser.ConfigParser()
config.read('config.ini')

ask_groups = json.loads(config.get('group-zone', 'ask'))
answer_groups = json.loads(config.get('group-zone', 'answer'))
total_groups = json.loads(config.get('group-zone', 'total'))

bot_ip = config.get('web', 'bot_ip')
global_ip = config.get('web', 'global_ip')

http_service_port = config.get('web', 'http_service_port')
http_website_port = config.get('web', 'http_website_port')


def get_group_name(group_id):
    url = f"http://{bot_ip}:{http_service_port}/get_group_info"
    payload = {
        "group_id": group_id
    }
    response = requests.post(url=url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            return data.get("data", {}).get("group_name", "未知群")
    return "未知群"


def get_user_name(group_id, user_id):
    url = f"http://{bot_ip}:{http_service_port}/get_group_member_info"
    payload = {
        "user_id": user_id,
        "group_id": group_id,
        "no_cache": True
    }
    response = requests.post(url=url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            return data.get("data", {}).get("card", "未知用户")
    return "未知用户"


# 将 question 转换为 markdown 格式（字符串）
def markdown_question(question_tuple):
    question_id, question_type, question_title, is_open, is_typical, is_unmeaningful, timestamp, group_id, user_id = question_tuple
    markdown = f"## Q{question_id}：{question_title} {{#q{question_id}}}\n\n"
    markdown += f"*来自群：{get_group_name(group_id)}  用户：{get_user_name(group_id, user_id)}  提问时间：{timestamp} 问题类别：{question_type}*\n\n"
    # 获取问题状态
    if is_open:
        markdown += "::: warning 问题状态：开放中\n:::\n\n"
    else:
        markdown += "::: info 问题状态：已关闭\n:::\n\n"
    if is_typical:
        markdown += "::: details\n这是一个典型问题，因此在你提问之前，请确保浏览过这些问题.\n:::\n\n"
    if is_unmeaningful:
        markdown += "::: danger\n这是一个无意义问题\n:::\n\n"
    # 获取该 question 的所有问题+追问追答内容
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT content, is_question, is_first, timestamp FROM questionNotes
        WHERE question_id = ? ORDER BY timestamp
    ''', (question_id,))
    for row in cursor.fetchall():
        content, is_question, is_first, timestamp = row
        if is_first:
            markdown += "**问题描述**：\n\n"
            markdown += get_raw_message(json.loads(content)) + "\n\n"
            markdown += "**追问追答**：\n\n"
        elif is_question and not is_first:
            markdown += f"***追问于：{timestamp}***\n\n"
            markdown += get_raw_message(json.loads(content)) + "\n\n"
        elif not is_question:
            markdown += f"::: tip ***追答于：{timestamp}***\n"
            markdown += get_raw_message(json.loads(content)) + "\n\n"
            markdown += ":::\n\n---\n\n"
    conn.commit()
    conn.close()
    return markdown


# 根据问题列表搭建网页（从头开始）
def website_build(qtype : str):
    md_path = f'./website/docs/{qtype}.md'
    # 获取全部 qtype 类问题
    chinese_type_name = {
        'document': "文档",
        'programming': "编程",
        'technology': "技术"
    }
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question_id, question_type, question_title, is_open, is_typical, is_unmeaningful, timestamp, group_id, user_id FROM questions
        WHERE question_type = ?
    ''', (qtype,))
    questions = cursor.fetchall()

    with open(md_path, 'w') as md:
        md.write(f"# {chinese_type_name[qtype]}类问题\n\n")
        for result in questions:
            md.write(markdown_question(result)) # 写入 md 文件

    # subprocess.run(['npm', 'run', 'docs:dev'])
    conn.commit()
    conn.close()
    
    pass


# 更新全部问题
def website_rebuild():
    for qtype in ['document', 'programming', 'technology']:
        website_build(qtype)
    # 典型问题、无意义问题和开放问题
    md_path = f'./website/docs/typical.md'
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question_id, question_type, question_title, is_open, is_typical, is_unmeaningful, timestamp, group_id, user_id FROM questions
        WHERE is_typical = 1
    ''')
    questions = cursor.fetchall()
    with open(md_path, 'w') as md:
        md.write(f"# 典型问题\n\n")
        for result in questions:
            md.write(markdown_question(result)) # 写入 md 文件
    md_path = f'./website/docs/unmeaningful.md'
    cursor.execute('''
        SELECT question_id, question_type, question_title, is_open, is_typical, is_unmeaningful, timestamp, group_id, user_id FROM questions
        WHERE is_unmeaningful = 1
    ''')
    questions = cursor.fetchall()
    with open(md_path, 'w') as md:
        md.write(f"# 无意义问题\n\n")
        for result in questions:
            md.write(markdown_question(result)) # 写入 md 文件
    md_path = f'./website/docs/open.md'
    cursor.execute('''
        SELECT question_id, question_type, question_title, is_open, is_typical, is_unmeaningful, timestamp, group_id, user_id FROM questions
        WHERE is_open = 1
    ''')
    questions = cursor.fetchall()
    with open(md_path, 'w') as md:
        md.write(f"# 开放问题\n\n")
        for result in questions:
            md.write(markdown_question(result)) # 写入 md 文件
    conn.commit()
    conn.close()


# 根据问题列表更新网页（追加 Q&A 页面）
def website_update():
    pass

