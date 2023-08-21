from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import pandas as pd
import random
import time
import sys
import requests
import os

# 指定.env文件的路径
dotenv_path = '.env'

# 加载.env文件中的环境变量
load_dotenv(dotenv_path)

# 访问.env文件中的环境变量
line_notify_token = os.getenv('LINE_NOTIFY_TOKEN')


def line_notify(message):
    # LINE Notify 權杖
    token = line_notify_token

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}
    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)


def get_chrome_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--incognito")  # 無痕模式
    chrome = webdriver.Chrome("/opt/chromedriver",
                              options=options)
    return chrome




def handler(event=None, context=None):
    driver = get_chrome_driver()
    URL = "https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates"  # 玉山匯率網址

    for retry in range(3):
        try:
            driver.get(URL)
            time.sleep(random.randrange(3, 5, 1))
            show_name = driver.find_elements(
                By.CLASS_NAME, 'area-figure.page-figure')
        except Exception:
            print('網頁載入失敗')
        else:
            if len(show_name) != 0:
                break

    # 初始化一个空的字典
    currency_dict = {}
    for i in range(len(driver.find_elements(By.CLASS_NAME, 'col-auto.px-3.col-lg-5.title-item'))):
        item_name = driver.find_elements(By.CLASS_NAME, 'col-auto.px-3.col-lg-5.title-item')[i].text
        BBoardRate = driver.find_elements(By.CLASS_NAME, 'BBoardRate')[i].text
        SBoardRate = driver.find_elements(By.CLASS_NAME, 'SBoardRate')[i].text
        BuyIncreaseRate = driver.find_elements(By.CLASS_NAME, 'BuyIncreaseRate')[i].text
        SellDecreaseRate = driver.find_elements(By.CLASS_NAME, 'SellDecreaseRate')[i].text
        CashBBoardRate = driver.find_elements(By.CLASS_NAME, 'CashBBoardRate')[i].text
        CashSBoardRate = driver.find_elements(By.CLASS_NAME, 'CashSBoardRate')[i].text
        # 将货币信息存储为字典
        currency_info = {
            '即期匯率買入': BBoardRate,
            '即期匯率賣出': SBoardRate,
            '網銀優惠買入': BuyIncreaseRate,
            '網銀優惠賣出': SellDecreaseRate,
            '現金買入': CashBBoardRate,
            '現金賣出': CashSBoardRate
        }
        
        # 将货币名和对应的信息存储到总的字典中
        currency_dict[item_name] = currency_info

    # 从总的字典中提取特定货币的信息
    currencies_to_extract = ['美元', '日圓']
    selected_currency_dict = {currency: currency_dict[currency] for currency in currencies_to_extract}

    message = ""
    for currency, info in selected_currency_dict.items():
        message += f"{currency}:\n"
        for key, value in info.items():
            message += f"{key}: {value}\n"
        message += "\n"

    line_notify("\n" + message)

    try:
        driver.quit()
    except Exception:
        print("browser不正常關閉")

