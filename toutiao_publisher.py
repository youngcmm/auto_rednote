import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import browser
import utils.util
from selenium.webdriver.common.action_chains import ActionChains
class TouTiaoPublisher():
    def __init__(self, cookie_file="cookies_toutiao.pkl", image_path=None, title="hello this is my first blog", content="I am a new one here, hello everybody!", topics_list = None, driver = None):
        self.driver = driver
        self.cookie_file = cookie_file # 加载Cookies文件路径
        self.image_path = image_path
        self.title = title
        self.content = content
        self.topics_list = topics_list 

    def load_cookies(self):
        # 加载之前保存的 小红书Cookies
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

    def send_title(self):
        # textarea = self.driver.find_element(
        #     By.CSS_SELECTOR, 
        #     "div.autofit-textarea-wrapper > textarea[placeholder='请输入文章标题（2～30个字）']"
        # )
        # # 通过 JavaScript 直接注入内容（绕过不可交互限制）
        # self.driver.execute_script(
        #     """
        #     // 同时设置 <pre> 和 <textarea> 的内容
        #     const title = arguments[0];
        #     const wrapper = arguments[1].closest('.autofit-textarea-wrapper');
        #     wrapper.querySelector('pre').textContent = title;
        #     wrapper.querySelector('textarea').value = title;
        #     // 触发输入事件确保页面响应
        #     wrapper.querySelector('textarea').dispatchEvent(new Event('input', { bubbles: true }));
        #     """,
        #     self.title,  # 要输入的标题文本
        #     textarea     # 定位到的 textarea 元素
        # )
        # 等待元素可交互并定位
        title_textarea = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'textarea[placeholder="请输入文章标题（2～30个字）"]')
            )
        )
        # 清空输入区域（如果已有内容）
        title_textarea.clear()
        # 输入新内容（假设content变量存储了要输入的字符串）
        title_textarea.send_keys(self.title)
        time.sleep(10)

    
    def input_content(self):
        # 使用更精准的CSS选择器定位编辑器
        editor = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                "div.syl-editor div.ProseMirror[contenteditable='true']"
            ))
        )
        # 生成符合数据结构的内容
        formatted_html = utils.util.convert_text_to_html(self.content)
        # 通过JavaScript注入内容
        self.driver.execute_script("""
            const editor = arguments[0];
            const newContent = arguments[1];
            // 插入新内容
            editor.innerHTML = newContent;
            
            // 触发完整事件链
            ['keydown', 'input', 'change', 'compositionend', 'blur'].forEach(eventName => {
                const event = new Event(eventName, { 
                    bubbles: true,
                    cancelable: true
                });
                editor.dispatchEvent(event);
            });
        """, editor, formatted_html)
        time.sleep(50)

    # def select_three_images(self):
    #     try:
    #         # 第一步：定位外层容器
    #         container = WebDriverWait(self.driver, 15).until(
    #             EC.presence_of_element_located((
    #                 By.XPATH, 
    #                 "//label[contains(@class,'byte-radio')]//span[contains(@class,'radio-inner-text') and contains(text(),'三图')]"
    #             ))
    #         )
    #         print("找到三图选项容器")

    #         # 第二步：等待元素可交互
    #         element = WebDriverWait(self.driver, 15).until(
    #             EC.element_to_be_clickable((
    #                 By.XPATH, 
    #                 "//label[contains(@class,'byte-radio')]//span[contains(text(),'三图')]/ancestor::label"
    #             ))
    #         )
    #         print("元素可交互状态确认")

    #         # 第三步：可视化操作
    #         self.driver.execute_script("arguments[0].style.border='2px solid red';", element)  # 调试标记
    #         self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
    #         # 第四步：点击操作
    #         print("尝试点击元素...")
    #         element.click()
    #         print("点击动作完成")

    #         # 第五步：验证选择状态
    #         WebDriverWait(self.driver, 5).until(
    #             lambda d: element.find_element(By.XPATH, ".//input").is_selected()
    #         )
    #         print("三图选项状态验证成功")

    #     except Exception as e:
    #         print("当前页面截图URL:", self.driver.current_url)
    #         print("页面HTML结构片段:", element.get_attribute('outerHTML')[:500] if 'element' in locals() else "未找到元素")
    #         raise Exception(f"选择三图失败: {str(e)}")
        
    def select_cover(self):
        try:
            # === 第一步：点击封面添加按钮 ===
            cover_trigger = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.byte-spin-container div.article-cover-add")
                )
            )
            # 使用JavaScript点击规避可能的遮挡
            self.driver.execute_script("arguments[0].click();", cover_trigger)
            print("已点击封面添加按钮")

            # === 第二步：切换至免费图片标签 ===
            free_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'byte-tabs-header-title') and text()='免费正版图片']")
                )
            )
            free_tab.click()
            print("已切换到免费正版图片标签")

            # === 第三步：输入搜索关键词 ===
            search_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[placeholder*='输入关键词组合']")
                )
            )
            # 先清空再输入（处理可能存在的默认值）
            search_input.clear()
            search_input.send_keys(self.topics_list[0])
            print(f"已输入关键词：{self.topics_list[0]}")

            # === 新增第四步：点击搜索按钮 ===
            search_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "span.btn-search")  # 根据实际结构可能需要调整选择器
                )
            )
            # 双重点击保障机制
            try:
                search_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", search_btn)
            print("已触发搜索操作")

            # === 第四步：选择第一个图片项 ===
            # 等待图片加载完成（通过检查loading消失）
            time.sleep(10)
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "div.loading-container")
                )
            )
            time.sleep(5)
            # 定位第一个可点击的图片项
            first_image = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "ul.list li.item")
                )
            )
            time.sleep(5)
            # 滚动到可视区域（处理懒加载）
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_image)
            # 添加点击容错机制
            for _ in range(3):
                try:
                    first_image.click()
                    break
                except:
                    self.driver.execute_script("arguments[0].click();", first_image)
            print("已选择首张图片")

            #第五步点击确定按钮
                # 等待 `确定` 按钮，并根据文本内容查找
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'byte-btn-primary') and span[text()='确定']]")
                )
            )
            confirm_button.click()
        except TimeoutException as e:
            print("操作超时，可能原因：")
            print("1. 图片加载时间过长")
            print("2. 元素定位器失效")
            print("3. 网络延迟异常")
            # 打印当前页面结构辅助调试
            print("当前页面HTML摘要：", self.driver.page_source[:1000])
            
        # finally:
        #     # 建议保持浏览器打开用于调试
        #     input("按回车键结束测试...")
    def click_the_AI_close_button(self):
        try:
            # 等待 `close-btn` 按钮出现
            close_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "close-btn"))
            )
            
            # 确保按钮可点击
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "close-btn")))
            
            # 点击按钮
            close_button.click()
            print("成功点击关闭按钮！")

        except Exception as e:
            print(f"关闭按钮不存在或不可点击: {e}")

    def select_img(self):
        count = 0 # 计数三次插入图片
        
        for i in range(len(self.topics_list)):
            time.sleep(5)
            try:
            #     # === 第一步：光标定位第一段末尾 ===
            #     target_paragraph = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR, "div.ProseMirror p[data-track='1']")
            #     )
            # )
            #     # 使用JavaScript设置光标到段落末尾
            #     driver.execute_script("""
            #         const paragraph = arguments[0];
            #         const range = document.createRange();
            #         const selection = window.getSelection();
                    
            #         // 定位到最后一个文本节点
            #         const lastChild = paragraph.lastChild;
            #         if(lastChild.nodeType === Node.TEXT_NODE) {
            #             range.setStart(lastChild, lastChild.length);
            #         } else {
            #             range.setStartAfter(paragraph.lastElementChild);
            #         }
                    
            #         range.collapse(true);
            #         selection.removeAllRanges();
            #         selection.addRange(range);
                    
            #         // 触发聚焦事件
            #         paragraph.parentElement.focus();
            #     """, target_paragraph)
                # 获取所有 <p> 元素
                p_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.ProseMirror p")
                # 创建 ActionChains
                actions = ActionChains(self.driver)
                # 点击第i段的末尾
                if len(p_elements) > 0 and count == 0 :
                    actions.move_to_element(p_elements[0]).click().perform()
                    count += 1 # count = 0+1
                    time.sleep(3)  # 等待1秒，确保点击生效
                    print('选中第一段')

                # 点击中间某个段落（这里选第 2 段，索引为 1）
                elif len(p_elements) > 4 and count == 1:  
                    actions.move_to_element(p_elements[5]).click().perform()
                    count += 1 # count = 1+1
                    time.sleep(3)  
                    print('选中第二段')

                # 点击最后一段的末尾（最后一个 <p> 之前的 <br> 可能是空行）
                elif len(p_elements) > 4 or count > 1: #第三次插入
                    actions.move_to_element(p_elements[-1]).click().perform()  # -2 避免选择空行的 <p><br></p>
                    time.sleep(3)  
                    print('选中第三段')
                    print('完成点击段的末尾插入')

                #第一步细分动作点击添加图片
                image_button = self.driver.find_element(By.CSS_SELECTOR, ".syl-toolbar-tool.image button")
                self.driver.execute_script("arguments[0].click();", image_button)
                time.sleep(2)
                # === 第二步：切换至免费图片标签 ===
                free_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(@class, 'byte-tabs-header-title') and text()='免费正版图片']")
                    )
                )
                free_tab.click()
                print("已切换到免费正版图片标签")

                # === 第三步：输入搜索关键词 ===
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "input[placeholder*='输入关键词组合']")
                    )
                )
                # 先清空再输入（处理可能存在的默认值）
                search_input.clear()
                search_input.send_keys(self.topics_list[i]) #搜素第i个话题
                print(f"已输入关键词：{self.topics_list[i]}")

                # === 新增第四步：点击搜索按钮 ===
                search_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "span.btn-search")  # 根据实际结构可能需要调整选择器
                    )
                )
                # 双重点击保障机制
                try:
                    search_btn.click()
                except:
                    self.driver.execute_script("arguments[0].click();", search_btn)
                print("已触发搜索操作")

                # === 第四步：选择第一个图片项 ===
                # 等待图片加载完成（通过检查loading消失）
                time.sleep(20)
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, "div.loading-container")
                    )
                )
                time.sleep(5)
                # 定位第一个可点击的图片项
                first_image = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "ul.list li.item")
                    )
                )
                time.sleep(5)
                # 滚动到可视区域（处理懒加载）
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_image)
                # 添加点击容错机制
                for _ in range(3):
                    try:
                        first_image.click()
                        break
                    except:
                        self.driver.execute_script("arguments[0].click();", first_image)
                print("已选择首张图片")

                #第五步点击确定按钮
                    # 等待 `确定` 按钮，并根据文本内容查找
                confirm_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'byte-btn-primary') and span[text()='确定']]")
                    )
                )
                confirm_button.click()
                time.sleep(5)
            except TimeoutException as e:
                print("操作超时，可能原因：")
                print("1. 图片加载时间过长")
                print("2. 元素定位器失效")
                print("3. 网络延迟异常")
                # 打印当前页面结构辅助调试
                print("当前页面HTML摘要：", self.driver.page_source[:1000])
            
        # finally:
        #     # 建议保持浏览器打开用于调试
        #     input("按回车键结束测试...")

    def pre_publish(self):
        try:
            # 使用 XPath 选择包含文本 '预览并发布' 的按钮
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'publish-btn-last') and span[text()='预览并发布']]"))
            )

            # 点击按钮
            publish_button.click()
            print("成功点击 '预览并发布' 按钮！")

        except Exception as e:
            print(f"未找到 '预览并发布' 按钮: {e}")
    
    def publish(self):
        try:
            # 使用 XPath 选择包含文本 '预览并发布' 的按钮
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'byte-btn-primary') and span[text()='确认发布']]"))
            )
            #<button class="byte-btn byte-btn-primary byte-btn-size-large byte-btn-shape-square publish-btn publish-btn-last" type="button"><span>确认发布</span></button>
            # 点击按钮
            publish_button.click()
            print("成功点击 '发布' 按钮！")

        except Exception as e:
            print(f"未找到 '发布' 按钮: {e}")
    def do(self, url='https://mp.toutiao.com/profile_v4/graphic/publish?from=toutiao_pc'):
        self.visit_page(url=url)
        self.load_cookies()
        self.input_content()
        self.click_the_AI_close_button()
        self.send_title()
        # self.select_cover()
        self.select_img()#选择三幅图
        time.sleep(10)
        self.pre_publish()
        time.sleep(30)
        self.publish()
        time.sleep(30)

if __name__ == "__main__":
    brow_instance = browser.Browser()
    driver = brow_instance.start_browser()
    toutiao_publish = TouTiaoPublisher(cookie_file="cookies_toutiao.pkl", 
                                 image_path=None, 
                                 title="46岁女教师炒股16年盈利113万！5%就卖的笨方法真能稳赚不赔？", 
                                 content="I am a new one here, hello everybody!\nI am a new one here, hello everybody!\nI am a new one here, hello everybody!I am a new one here, hello everybody!\nI am a new one here, hello everybody!\nI am a new one here, hello everybody!I am a new one here, hello everybody!\nI am a new one here, hello everybody!\nI am a new one here, hello everybody!", 
                                 topics_list = ['枪支管制', '心理健康', '好莱坞内幕'], 
                                 driver = driver)
    toutiao_publish.do()
    # toutiao_publish.select_three_images()


