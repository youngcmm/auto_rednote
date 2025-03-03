from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pickle
import utils

class XiaohongshuPublisher:
    def __init__(self, cookie_file="cookies.pkl", image_path=None, title="hello this is my first blog", content="I am a new one here, hello everybody!", topics_list = None):
        # 设置浏览器选项
        self.options = Options()
        # self.options.add_argument('--headless')  # 无头模式（后台运行）
        self.options.add_argument('--disable-gpu')  # 禁用 GPU 加速
        self.options.add_argument('--no-sandbox')  # 避免沙盒问题

        # 启动 WebDriver
        self.driver = webdriver.Chrome(options=self.options)

        # 加载Cookies文件路径
        self.cookie_file = cookie_file
        self.image_path = image_path
        self.title = title
        self.content = content
        self.topics_list = topics_list 

    def load_cookies(self):
        # 加载之前保存的 Cookies
        cookies = pickle.load(open(self.cookie_file, "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        # 刷新页面，确保 Cookies 生效
        self.driver.refresh()
        time.sleep(30)

    def visit_page(self, url):
        # 访问页面
        self.driver.get(url)
        # 等待页面加载
        # time.sleep(3)  # 或者使用 WebDriverWait

    def click_upload_tab(self):
        # 2. 点击“上传图文”
        upload_tab = self.driver.find_element(By.XPATH, "//div[@class='creator-tab']//span[text()='上传图文']")
        upload_tab.click()
        time.sleep(5)

    def upload_image(self):
        # 3. 上传首张图片
        upload_input = self.driver.find_element(By.XPATH, "//input[@class='upload-input']")
        upload_input.send_keys(self.image_path)  # 使用实例传入的图片路径
        time.sleep(20)  # 等待图片上传

    def fill_title(self):
        # 4. 填入标题
        title_input = self.driver.find_element(By.XPATH, "//input[@class='d-text']")
        # title_input.send_keys(self.title)
        self.driver.execute_script(
        "arguments[0].value = arguments[1];", 
        title_input,
        self.title  # 包含特殊字符的原始文本
    )

    def fill_content(self):
        # # 5. 填入内容
        # content_input = self.driver.find_element(By.ID, "quillEditor").find_element(By.CLASS_NAME, "ql-editor")
        # # 点击编辑区域聚焦
        # content_input.click()
        # # 输入内容
        # content_input.send_keys(self.content)

        # 5. 填入内容（JavaScript方案）
        html_content = utils._convert_text_to_html(self.content) #str转为html
        editor = self.driver.find_element(By.ID, "quillEditor").find_element(By.CLASS_NAME, "ql-editor")
        # 通过JavaScript设置富文本HTML内容
        self.driver.execute_script(
            """
            // 清空原有内容
            arguments[0].innerHTML = arguments[1];
            // 触发编辑器更新事件
            const event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
            """,
            editor,
            html_content
        )
        time.sleep(10)  # 等待内容填充

    def activate_topics(self):
        editor = self.driver.find_element(By.CLASS_NAME, 'ql-editor')
        
        for topic in self.topics_list:
            # 确保话题带#号
            search_text = f"#{topic.strip()}"
            
            # 通过XPath定位精确的文本节点
            topic_element = self.driver.find_element(
                By.XPATH, f"//*[contains(@class,'ql-editor')]//text()[contains(., '{search_text}')]/parent::*"
            )
            
            # 执行核心操作
            self.driver.execute_script("""
                const [element, topicText] = arguments;
                
                // 1. 定位精确的文本节点
                const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
                let targetNode = null;
                
                while(walker.nextNode()) {
                    if(walker.currentNode.textContent.includes(topicText)) {
                        targetNode = walker.currentNode;
                        break;
                    }
                }
                
                if(!targetNode) return;
                
                // 2. 设置光标位置
                const range = document.createRange();
                const offset = targetNode.textContent.indexOf(topicText) + topicText.length;
                range.setStart(targetNode, offset);
                range.setEnd(targetNode, offset);
                
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                
                // 3. 模拟用户交互
                element.dispatchEvent(new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
                
                // 4. 添加5秒延迟后再触发回车
                setTimeout(() => {
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    });
                    element.dispatchEvent(enterEvent);
                }, 5000); 
                // 5. 强制布局更新
                element.scrollIntoView({behavior: 'auto', block: 'center'});
            """, topic_element, search_text)
            
            time.sleep(5)  # 操作间隔

    def click_publish_button(self):
        # 7. 点击发布按钮
        publish_button = self.driver.find_element(By.CLASS_NAME, "publishBtn")
        publish_button.click()
        time.sleep(5)  # 等待页面反应

    def close_browser(self):
        # 关闭浏览器
        self.driver.quit()

    def publish(self, url):
        # 执行整个发布流程
        self.visit_page(url)
        self.load_cookies()
        self.click_upload_tab()
        self.upload_image()
        self.fill_title()
        self.fill_content()
        self.activate_topics()
        self.click_publish_button()
        self.close_browser()

# 使用类发布
if __name__ == "__main__":
    publisher = XiaohongshuPublisher(cookie_file='cookies.pkl', image_path="/Users/ycm/Desktop/图片_硕士毕业论文_dcgc/QX-Trachea_convergencen.png", title='🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？', content='🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？\n 🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？')
    publisher.publish(url="https://creator.xiaohongshu.com/publish/publish?source=official")