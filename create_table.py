import sqlite3
import configparser
import json
import requests

config = configparser.ConfigParser()
config.read('config.ini')

bot_ip = config.get('web', 'bot_ip')
http_service_port = config.get('web', 'http_service_port')

ask_groups = json.loads(config.get('group-zone', 'ask'))
assistant_groups = json.loads(config.get('group-zone', 'assistant'))


def create_table():
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS messages
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER UNIQUE,
            group_id INTEGER,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT
        )
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS users
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,  -- 工号或学号
            qq_id INTEGER UNIQUE,  -- QQ号
            username TEXT,
            user_type TEXT,  -- 例如：老师、助教、学生
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS groups
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER UNIQUE,
            group_name TEXT,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS questionNotes
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionNotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            message_id INTEGER UNIQUE,
            content TEXT,
            is_question BOOLEAN,
            is_first BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            group_id INTEGER,
            user_id INTEGER
        )
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS questions
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT,
            question_title TEXT DEFAULT "未命名问题",
            is_open BOOLEAN DEFAULT 1,
            is_typical BOOLEAN DEFAULT 0,
            is_unmeaningful BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            group_id INTEGER,
            user_id INTEGER
        )
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS questionIds
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionIds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER UNIQUE,
            question_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def insert_users():
    # 需要导入用户信息表格（身份：老师、助教、学生，暂无数据）
    # 仅测试
    users = [
        (11111, 278787983, '沈坚', '老师')
    ]
    for group_id in assistant_groups:
        url = f"http://{bot_ip}:{http_service_port}/get_group_member_list"
        payload = {
            'group_id': group_id
        }
        responce = requests.post(url=url, json=payload)
        if responce.status_code == 200:
            data = responce.json()
            for row in data['data']:
                if len(row['card'].split('-')) == 3:
                    stu_no, _, stu_name = row['card'].split('-') 
                    q_no = row['user_id']
                    users.append((stu_no, q_no, stu_name, '助教'))

    for group_id in ask_groups[5:6]:
        url = f"http://{bot_ip}:{http_service_port}/get_group_member_list"
        payload = {
            'group_id': group_id
        }
        responce = requests.post(url=url, json=payload)
        if responce.status_code == 200:
            data = responce.json()
            for row in data['data']:
                if len(row['card'].split('-')) == 3:
                    stu_no, _, stu_name = row['card'].split('-') 
                    q_no = row['user_id']
                    if (stu_no, q_no, stu_name, '助教') not in users:
                        users.append((stu_no, q_no, stu_name, '学生'))
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT OR IGNORE INTO users (user_id, qq_id, username, user_type) VALUES (?, ?, ?, ?)', users)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    insert_users()
