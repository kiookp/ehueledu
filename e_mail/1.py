import time
import requests
import json
import random
import string
import configparser
import pyperclip
import subprocess

def generate_username(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def set_account_attrs(config, email):
    sid = config.get('Credentials', 'sid')
    Coremail = config.get('Credentials', 'Coremail')
    uid = config.get('Credentials', 'uid')

    url = f'http://mail.stu.huel.edu.cn/coremail/s/json?sid={sid}&func=user%3AsetAcountAttrs'
    headers = {
        'Accept': 'text/x-json',
        'Content-Type': 'text/x-json',
        'Referer': f'http://mail.stu.huel.edu.cn/coremail/XT5/index.jsp?sid={sid}',
        'Origin': 'http://mail.stu.huel.edu.cn',
        'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    cookies = {
        'Coremail.sid': sid,
        'CoremailReferer': 'http%3A%2F%2Fmail.stu.huel.edu.cn%2Fcoremail%2Findex.jsp%3F',
        'Coremail': Coremail,
        'saveUsername': 'true',
        'domain': 'stu.huel.edu.cn',
        'locale': 'zh_CN',
        'uid': f'{uid}%40stu.huel.edu.cn',
        'face': 'auto'
    }

    payload = json.dumps({"attrs": {"alias_attrs": email}})

    response = requests.post(url, headers=headers, cookies=cookies, data=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 'S_OK':
            print(f"创建成功，新建别名: {email}")
            pyperclip.copy(email)  # 复制别名到剪贴板
            print("别名已复制到剪贴板")

            # 保存别名到配置文件
            config.set('Credentials', 'email', email)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        else:
            print(f"请求失败: {data.get('msg')}")
    else:
        print('请求失败:', response.status_code)

def receive_email():
    subprocess.run(['python', 'reemail.py'])

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    email = config.get('Credentials', 'email', fallback='')

    while True:
        print("1. 随机生成username")
        print("2. 手动输入username")
        print("3. 收取邮件")
        print("4. 退出程序")
        choice = input("请输入你的选择(1/2/3/4): ")
        if choice == '1':
            username = generate_username()
            print(f"生成的username为: {username}")
            email = f"{username}@stu.huel.edu.cn"
            set_account_attrs(config, email)
        elif choice == '2':
            email = input("请输入email: ")
            set_account_attrs(config, email)
        elif choice == '3':
            print("等待6秒...")
            time.sleep(6)
            receive_email()
        elif choice == '4':
            break
        else:
            print("无效的输入，请重新输入")

if __name__ == "__main__":
    main()
