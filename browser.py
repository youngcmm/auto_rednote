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
    
    def start_browser(self):
        # 启动 WebDriver
        self.driver = webdriver.Chrome(options=self.options)
        return self.driver
    
    def close(self):
        self.driver.quit()   