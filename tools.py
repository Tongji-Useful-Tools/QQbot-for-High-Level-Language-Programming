import re

def get_raw_message(message : list) -> str:
    raw_message = ""
    for item in message:
        if item["type"] == "text":
            raw_message += item["data"]["text"]
        elif item["type"] == "at":
            raw_message += f"@{item['data']['qq']} "
        elif item["type"] == "image":
            raw_message += "[图片] "
        elif item["type"] == "face":
            raw_message += f"[表情{item['data']['id']}] "
        # 可以根据需要添加更多类型的处理
    return raw_message.strip()


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
            item["data"]["text"] = re.sub(rf"[qQ]\s*{number}", "", item["data"]["text"])

        new_message.append(item)

    return new_message
