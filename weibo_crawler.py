from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import json
import requests
import browser
import utils.util
class WeiboCrawler:
    def __init__(self, driver):
        self.content_url = None
        self.driver = driver
        #后台request直接访问文娱热榜
        self.url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Dfun&page_type=08"
        # 设置 User-Agent 头部，模拟浏览器访问
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://m.weibo.cn/"
        }

    def get_hot_list(self):
        # 发送 GET 请求
        response = requests.get(self.url, headers=self.headers)
        # 判断是否成功
        if response.status_code == 200:
            json_data = response.json()  # 解析 JSON
            # print(json_data)  # 输出 JSON 数据
        else:
            print("请求失败，状态码：", response.status_code)
        self.card_group = json_data['data']['cards'][0]['card_group']
        # desc = card_group[0]['desc'] #热榜话题地址
        # scheme = card_group[0]['scheme'] #热榜标题
        return self.card_group
        

    def fetch_content(self, content_url):
        # 访问目标 URL
        self.driver.get(content_url)
        # 等待加载
        time.sleep(3) 
        # 获取页面内容（JSON 字符串）
        app_div = self.driver.find_element(By.ID, "app")
        weibo_content = app_div.get_attribute("outerHTML")
        # 将内容保存到文件
        # with open("weibo_app_content.txt", "w", encoding="utf-8") as file:
            # file.write(weibo_content)
        # print("数据已保存到 weibo_app_content.txt")
        return weibo_content


    def close(self):
        self.driver.quit()

    def crawl(self, content_url):
        weibo_content = self.fetch_content(content_url)
        return weibo_content
    
    def do(self):
        '''
        返回内容和标题
        '''
        cards = self.get_hot_list()
        weibo_conten = self.crawl(content_url=cards[0]['scheme'])
        return weibo_conten, {'title':cards[0]['desc']} #这里转为字典格式，和后面的生成相对应

# #爬取微博内容
# answer_txt_list = []
# question_list = []
# driver = browser.Browser()
# browser_instance = driver.start_browser()
# crawler = WeiboCrawler(driver=browser_instance)
# # answer_txt, question = crawler.do()
# hot_list = crawler.get_hot_list()
# for i in range(2): #爬取执行两次
#     answer_txt = crawler.fetch_content(content_url=hot_list[i]['scheme'])
#     question = {'title':hot_list[i]['desc']}
#     answer_txt_list.append(answer_txt)
#     question_list.append(question)
#     ext_comments = utils.util.extract_weibo_comments(html_str=answer_txt)
#     print('\r\n'.join(ext_comments))
#     print(question)
# browser_instance.close()
