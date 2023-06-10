import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import telebot
import undetected_chromedriver as uc
import configparser
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

config = configparser.ConfigParser()
config.read('config.ini')

telegram_bot_token = config['Credentials']['telegram_bot_token']
telegram_chat_id = config['Credentials']['telegram_chat_id']
website = config['Credentials']['website']
username = config['Credentials']['username']
password = config['Credentials']['password']

def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id, message)
        print(f"消息已发送 ")
    except Exception as e:
        print(f"无法发送消息：{e}")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-setuid-sandbox")
driver = uc.Chrome(options=chrome_options)

driver.get(website)
print("成功打开网站")

wait = WebDriverWait(driver, 30)

uid_input = wait.until(EC.presence_of_element_located((By.NAME, "uid")))

uid_input.clear()
uid_input.send_keys(username)

print("成功输入账号")

password_input = wait.until(EC.presence_of_element_located((By.ID, "fakePassword")))

password_input.send_keys(password)
print("成功输入密码")

login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[3]/div[1]/form/div[3]/button")))

try:
    login_button.click()
    error_label_locator = (By.XPATH, "//*[@id='warnOrErrDiv']/label")
    success_element_locator = (By.XPATH, "/html/body/section/article")
    bind_phone_element_locator = (By.XPATH, "//*[@id='body_area']/form/div[1]/table/tbody/tr/td/input")
    cancel_button_locator = (By.XPATH, "//*[@id='body_area']/form/div[2]/div/div[2]")

    try:
        wait.until(EC.visibility_of_element_located(success_element_locator))
        print("登录成功！")
        bot = telebot.TeleBot(telegram_bot_token)
        send_telegram_message(bot, telegram_chat_id, f"账号 {username}：登录成功!")

        cookies = driver.get_cookies()

        coremail_sid = None
        coremail = None

        for cookie in cookies:
            if cookie['name'] == 'Coremail.sid':
                coremail_sid = cookie['value']
            elif cookie['name'] == 'Coremail':
                coremail = cookie['value']

        print("Coremail.sid:", coremail_sid)
        print("Coremail:", coremail)
        print("uid:", username)
        print("开始保活...")
        send_telegram_message(bot, telegram_chat_id, "开始保活...")

        message = f"Coremail.sid: {coremail_sid}\nCoremail: {coremail}"
        send_telegram_message(bot, telegram_chat_id, message)

        while True:
            try:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_2_span"))).click()
                time.sleep(60)

                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_3_span"))).click()
                time.sleep(60)

                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_4_span")))
                driver.refresh()
                time.sleep(10)

            except Exception as e:
                print("出现异常：", str(e))
                print("正在刷新页面...")
                driver.refresh()

    except TimeoutException:
        if driver.find_elements(*bind_phone_element_locator):
            print("需要绑定手机号！以跳过")
            cancel_button = driver.find_element(*cancel_button_locator)
            cancel_button.click()
            try:
                wait.until(EC.visibility_of_element_located(success_element_locator))
                print("登录成功！")
                bot = telebot.TeleBot(telegram_bot_token)
                send_telegram_message(bot, telegram_chat_id, f"账号 {username}：登录成功!")

                cookies = driver.get_cookies()

                coremail_sid = None
                coremail = None

                for cookie in cookies:
                    if cookie['name'] == 'Coremail.sid':
                        coremail_sid = cookie['value']
                    elif cookie['name'] == 'Coremail':
                        coremail = cookie['value']

                print("Coremail.sid:", coremail_sid)
                print("Coremail:", coremail)
                print("uid:", username)
                print("开始保活...")
                send_telegram_message(bot, telegram_chat_id, "开始保活...")

                message = f"Coremail.sid: {coremail_sid}\nCoremail: {coremail}"
                send_telegram_message(bot, telegram_chat_id, message)

                while True:
                    try:
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_2_span"))).click()
                        time.sleep(60)

                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_3_span"))).click()
                        time.sleep(60)

                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#mltree_4_span")))
                        driver.refresh()
                        time.sleep(10)

                    except Exception as e:
                        print("出现异常：", str(e))
                        print("正在刷新页面...")
                        driver.refresh()

            except TimeoutException:
                print("登录失败！")
                bot = telebot.TeleBot(telegram_bot_token)
                send_telegram_message(bot, telegram_chat_id, "登录失败！")

        elif driver.find_elements(*error_label_locator):
            print("账号或密码错误，登录失败！")
            bot = telebot.TeleBot(telegram_bot_token)
            send_telegram_message(bot, telegram_chat_id, "账号或密码错误，登录失败！")
        else:
            print("登录失败！")
            bot = telebot.TeleBot(telegram_bot_token)
            send_telegram_message(bot, telegram_chat_id, "登录失败！")

except WebDriverException as e:
    print("登录过程中出现异常:", str(e))

finally:
    driver.quit()
