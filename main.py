from datetime import datetime
from zhihu_crawler import fetch_zhihu_hot, fetch_zhihu_hot_answer_by_jina
from xiaohongshu_publisher import XiaohongshuPublisher
from config import DEEPSEEK_CONFIG  # 简化配置导入
import config
from openai import OpenAI
import weibo_crawler
import imgrender 
client = OpenAI(
    api_key=DEEPSEEK_CONFIG["api_key"],
    base_url=DEEPSEEK_CONFIG["base_url"]
)
import json
import re
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import random
from datetime import datetime, timedelta
import browser
from utils.util import *
import schedule
import time
from datetime import datetime
import logging
import time

def generate_content(question, answer_txt, template_key="rednote"):
    """使用模板生成小红书内容"""
    try:
        # 加载提示词模板
        try:
            with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
                system_prompt = f.read().format(
                    topic=question['title'],
                    original_text=answer_txt  # 使用从知乎获取的实际回答内容
                )
        except:
            with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
                system_prompt = f.read().format(
                    questions_list = question #这里是判断筛选主题的任务的提示词，替换掉提示词中的内容
                )
        
        # print(system_prompt)
        completion = client.chat.completions.create(
            model=DEEPSEEK_CONFIG["model"],
            temperature=DEEPSEEK_CONFIG["temperature"],
            # max_tokens=DEEPSEEK_CONFIG["max_tokens"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请根据以上要求生成内容"}
            ]
        )
        return completion
        # return utils.add_hashtags(completion.choices[0].message.content)
    except Exception as e:
        print(f"内容生成失败: {str(e)}")
        return None

def job():

    # # 获取知乎热榜
    # hot_questions = fetch_zhihu_hot()
    # if not hot_questions:
    #     print("未获取到热榜数据")
    #     return
    # # 获取当前热榜问题
    # question = hot_questions[0]
    # # 使用jina获取高赞回答
    # answer_txt = fetch_zhihu_hot_answer_by_jina(question['url'])
    # if not answer_txt:
    #     print("获取回答内容失败")
    #     return
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始执行任务")
        #爬取微博内容
        answer_txt_list = []
        question_list = []
        driver = browser.Browser()
        browser_instance = driver.start_browser()
        crawler = weibo_crawler.WeiboCrawler(driver=browser_instance)
        # answer_txt, question = crawler.do()
        hot_list = crawler.get_hot_list()
        for i in range(2): #爬取执行两次
            answer_txt = crawler.fetch_content(content_url=hot_list[i]['scheme'])
            question = {'title':hot_list[i]['desc']}
            ext_comments = extract_weibo_comments(html_str=answer_txt) #从提取前端页面提取评论
            answer_txt_list.append('\r\n'.join(ext_comments)) #多条评论换行拼接。
            question_list.append(question)
        browser_instance.close()

        for i in range(2): #发布执行两次
            question = question_list[i]
            answer_txt = answer_txt_list[i]
            time_ymd = time.strftime("%Y%m%d", time.localtime()) #时间
            save_content(content=answer_txt, path=f"output_files/{time_ymd}/{question}/answer_txt.txt") #存储爬取到的回答
            # # 第一步提炼观点
            # template_key = "controversy_extract"
            # # 生成内容时传递完整参数
            # controversy_content = generate_content(question, answer_txt, template_key)
            # if not controversy_content:
            #     print("观点提炼失败")
            #     return
            # # 使用示例
            # status, result = extract_json_from_response(controversy_content)
            # if status:
            #     print("提取成功！")
            #     print("核心争议:", result['core_controversies'])
            #     print("热门标签:", result['hot_tags'])
            # else:
            #     print("错误:", result)

            # 第二步生成小红书内容
            # template_key = "rednote"
            # 将争议观点从List变为字符串
            # controversies_str = "\n".join([f"- {item}" for item in result['core_controversies']])
            # 加载生成提示词模版
            # with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
            #     # 读取模板内容
            #     template_content = f.read()
            #     # 格式化提示词
            #     system_prompt = template_content.format(
            #     topic=question['title'],
            #     original_text=answer_txt,
            #     controversy_content=controversies_str  # 注意模板中要对应 {controversy_content}
            # )
            template_key = 'weibo_to_xiaohongshu_english'
            # 搬运微博文娱道小红书 
            with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
                # 读取模板内容
                template_content = f.read()
                # 格式化提示词
                system_prompt = template_content.format(
                topic=question['title'],
                original_text=answer_txt,
            )
            # 保存到新文件（避免覆盖原模板）
            output_path = f"prompts/generated_{template_key}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(system_prompt)
            
            # 生成内容时传递完整参数
            content = generate_content(question, answer_txt, f'generated_{template_key}')
            if not content:
                print("内容生成失败")
                return
            content = extract_post_content(content) #从大模型中返回结果提取content
            print('小红书内容：')
            print(content)
            save_content(content=content, path=f"output_files/{time_ymd}/{question}/content.txt") #存储大模型返回的内容
            split_content = content.split('\n\n') #分割内容，将英文抽离出来
            res_conten = ''
            for i in range(len(split_content)):
                if i!=0: #排除掉英文
                    if res_conten:
                        res_conten = res_conten+'\n\n'+split_content[i] #排除掉中文翻译
                    else:
                        res_conten = split_content[i] # res_content为空的时候直接不加\n\n
            content = res_conten + '\n\n #英语学习打卡 #四六级 #娱乐圈'
            last_line = get_last_line(content) #取得最后一行，话题
            last_line = last_line.split('#') #把最后一行每一个话题list化
            last_line = [item for item in last_line if item] #去掉空的话题

            #第三步，根据生成的小红书内容提取第一行小红书标题
            title = get_first_line(content)
            print('小红书标题：')
            print(title)

            #第四步根据tile生成封面图
            # txt2img.paint_dance(desc=title, img_name='title')
            # imgrender_instance_png0 = imgrender.ImgReder(txt='娱乐狗腿子学英语：'+question['title'], payload_chinese=False, down_path='title.png')
            # imgrender_instance_png0.do()

            imgrender_instance_png1 = imgrender.ImgReder(txt=split_content[0], payload_chinese=True, down_path='title.png') #生成英文的图片
            imgrender_instance_png1.do()

            # imgrender_instance = imgrender.ImgReder(txt=split_content[4],payload_chinese=True, down_path='title2.png') #生成文化贴士的图片
            # imgrender_instance.do()
            
            # 小红书发布
            driver = browser.Browser()
            driver = driver.start_browser()
            xiaohongshu_publisher = XiaohongshuPublisher(cookie_file='cookies.pkl', image_path='/Users/ycm/Desktop/code/auto/title.png', title=title, content=content, topics_list = last_line, driver=driver)
            xiaohongshu_publisher.publish(url=config.PUBLISH_URL)
            try:
                driver.close()
            except:
                pass
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 任务执行成功")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 任务执行失败: {str(e)}")
        print("10秒后重试...")
        time.sleep(10)
        
        job()  # 失败后自动重试一次
            
if __name__ == "__main__":
    # 设置定时任务
    schedule.every().day.at("09:02").do(job)  # 上午9点执行
    schedule.every().day.at("12:02").do(job)  # 中午12点执行
    schedule.every().day.at("18:02").do(job)  # 下午6点执行

    print("定时任务已启动，每天12:02和18:02自动执行")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次
    # job()
