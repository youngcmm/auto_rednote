from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
class Browser:
    def __init__(self):
                # 设置浏览器选项
        self.options = Options()
        # self.options.add_argument('--headless')  # 无头模式（后台运行）
        self.options.add_argument('--disable-gpu')  # 禁用 GPU 加速
        self.options.add_argument('--no-sandbox')  # 避免沙盒问题
        self.options.add_argument("--disable-notifications") # 禁用通知
        self.options.add_argument("--log-level=3")           # 禁用日志输出
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        # prefs = {
        #     "profile.managed_default_content_settings.images": 2,
        #     "profile.managed_default_content_settings.stylesheet": 2,
        # }
        # self.options.add_experimental_option("prefs", prefs)
        self.options.add_argument("--log-level=3")           # 禁用日志输出
    def start_browser(self):
        # 启动 WebDriver
        self.driver = webdriver.Chrome(options=self.options)
        return self.driver
    
    def close(self):
        self.driver.quit()   