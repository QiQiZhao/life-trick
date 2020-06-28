import os
from selenium import webdriver
import datetime
import time

def login():
    # 打开淘宝首页，通过扫码登录
    browser.get("https://www.taobao.com")
    time.sleep(3)
    if browser.find_element_by_link_text("亲，请登录"):
        browser.find_element_by_link_text("亲，请登录").click()
        print(f"请尽快扫码登录")
        time.sleep(10)

def buy():
    browser.get("https://cart.taobao.com/cart.htm")
    time.sleep(3)
    while True:
        try:
            if browser.find_element_by_id("J_SelectAll1"):
                browser.find_element_by_id("J_SelectAll1").click()
                break
        except:
            print(f"找不到购买按钮")
    while True:
        while True:
            try:
                if browser.find_element_by_id("J_Go"):
                    browser.find_element_by_id("J_Go").click()
                    print(f"结算成功，准备提交订单")
                    time.sleep(0.5)
                    break
            except:
                pass
            # 点击提交订单按钮
        while True:
            try:
                if browser.find_element_by_link_text('提交订单'):
                    browser.find_element_by_link_text('提交订单').click()
                    print(f"抢购成功，请尽快付款")
            except:
                print(f"再次尝试提交订单")
        time.sleep(0.01)

if __name__ == "__main__":
	browser = webdriver.Chrome()
	browser.maximize_window()
	login()
	buy()