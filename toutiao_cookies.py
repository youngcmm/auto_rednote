from selenium import webdriver
import pickle
import time
import browser

# 启动 WebDriver
browser_instance = browser.Browser()
driver = browser_instance.start_browser()

# 访问页面并手动登录一次
driver.get("https://mp.toutiao.com/profile_v4/graphic/publish")
time.sleep(100)  # 给你足够的时间手动登录并通过手机号验证

# 保存 Cookies 到文件
pickle.dump(driver.get_cookies(), open("cookies_toutiao.pkl", "wb"))
driver.close()  # 退出浏览器
