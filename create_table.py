import sqlite3

def create_table():
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            qq_id BIGINT UNIQUE,  -- QQ号
            username TEXT,
            user_type TEXT,  -- 例如：老师、助教、学生
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP
        )
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
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER UNIQUE,
            content TEXT,
            is_question BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            group_id INTEGER,
            user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def insert_users():
    conn = sqlite3.connect('llbot.db')
    cursor = conn.cursor()
    # 需要导入用户信息表格（身份：老师、助教、学生，暂无数据）
    # 仅测试
    users = [
        (2353367, 1905996217, '肖家余', '助教'),
        (2451918, 3611514898, '牛玥茗', '学生'),
        (11111, 1234567890, '未知用户', '老师')
    ]
    cursor.executemany('INSERT OR IGNORE INTO users (user_id, qq_id, username, user_type) VALUES (?, ?, ?, ?)', users)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    insert_users()
