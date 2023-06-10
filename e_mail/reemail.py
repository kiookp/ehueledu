import imaplib
import email
import re
import datetime
import time
import pyperclip
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

email_address = config.get('Credentials', 'email', fallback='')
mail_host = config.get('Credentials', 'mail_host', fallback='')
password = config.get('Credentials', 'password', fallback='')

if not email_address or not mail_host or not password:
    print("配置文件中缺少参数，请先设置 [Credentials] 段中的 email、mail_host 和 password 参数。")
    exit()

username = email_address.split('@')[0]

M = imaplib.IMAP4(mail_host, 143)
M.login(email_address, password)

max_retries = 8
retry_count = 0

while retry_count < max_retries:
    M.select('INBOX')

    status, data = M.search(None, 'ALL')
    latest_email_id = data[0].split()[-1]

    status, msg_data = M.fetch(latest_email_id, '(RFC822)')
    raw_email = msg_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    subject = email_message['Subject']
    decoded_subject = email.header.decode_header(subject)
    decoded_text = decoded_subject[0][0]
    decoded_charset = decoded_subject[0][1]

    date = email.utils.parsedate_to_datetime(email_message['Date'])
    new_date = date + datetime.timedelta(hours=15)
    formatted_date = new_date.strftime("%Y-%m-%d %H:%M:%S")
    print("邮件时间:", formatted_date)

    current_time = datetime.datetime.now()
    print("当前查找的时间:", current_time.strftime("%Y-%m-%d %H:%M:%S"))

    if formatted_date <= current_time.strftime("%Y-%m-%d %H:%M:%S"):
        found_links = []
        for part in email_message.walk():
            if part.get_content_type() == "text/html":
                content = part.get_payload(decode=True)
                decoded_content = content.decode(part.get_content_charset() or 'utf-8', errors='replace')

                pattern = r'href="(.*?)"'
                links = re.findall(pattern, decoded_content)
                for link in links:
                    if link.startswith("https://verifyemail.microsoft.com/v1.0/tokenverification/verify?"):
                        found_links.append(link)

        if found_links:
            found_links.sort(reverse=True)
            found_link = found_links[0]
            print("找到的链接:", found_link)
            pyperclip.copy(found_link)

            print("链接已复制到剪贴板")
            break
        else:
            print("未找到链接")
    else:
        print("时间不符合要求")

    retry_count += 1
    if retry_count < max_retries:
        print(f"等待10秒后进行第 {retry_count + 1} 次查询...")
        time.sleep(10)

M.logout()
