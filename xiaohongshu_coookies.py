from selenium import webdriver
import pickle
import time

# 启动 WebDriver
driver = webdriver.Chrome()

# 访问页面并手动登录一次
driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
time.sleep(100)  # 给你足够的时间手动登录并通过手机号验证

# 保存 Cookies 到文件
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
driver.quit()  # 退出浏览器
