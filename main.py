from datetime import datetime
from zhihu_crawler import fetch_zhihu_hot, fetch_zhihu_hot_answer_by_jina
# from xhs_poster import XHSPoster
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
scheduler = BlockingScheduler(timezone="Asia/Shanghai")  # 设置时区

def schedule_random_job(hour):
    # 生成0到15分钟的随机延迟（单位：秒）
    delay = random.randint(0, 3 * 60)
    run_time = datetime.now() + timedelta(seconds=delay)
    scheduler.add_job(job, 'date', run_date=run_time)
    print(f"任务将在 {run_time.strftime('%H:%M:%S')} 执行")

def check_initial_schedule():
    now = datetime.now()
    # 检查中午时间段
    if 12 <= now.hour < 12 and 0 <= now.minute < 3:
        remaining = (datetime(now.year, now.month, now.day, 12, 3) - now).total_seconds()
        delay = random.uniform(0, remaining)
        scheduler.add_job(job, 'date', run_date=now + timedelta(seconds=delay))
    # 检查下午时间段
    if 18 <= now.hour < 18 and 0 <= now.minute < 3:
        remaining = (datetime(now.year, now.month, now.day, 18, 3) - now).total_seconds()
        delay = random.uniform(0, remaining)
        scheduler.add_job(job, 'date', run_date=now + timedelta(seconds=delay))

def get_last_line(s):
    lines = s.splitlines()
    return lines[-1] if lines else ''

def get_first_line(s):
    lines = s.splitlines()
    return lines[0] if lines else ''

def extract_post_content(chat_completion_response):
    """
    从大模型返回的响应中提取并清理<post>标签内的内容
    返回: 清理后的字符串（去除转义符和标记）
    """
    try:
        # 获取原始内容字符串
        raw_content = chat_completion_response.choices[0].message.content
        
        # 提取<post>标签内容（含安全处理）
        post_content = re.search(r'<post>\n?(.*?)\n?</post>', raw_content, re.DOTALL).group(1)
        
        # # 清理转义字符和多余换行
        # cleaned_content = post_content.replace('\\n', '\n').strip()
        
        return post_content
    
    except AttributeError:
        print("错误：未找到<post>标签包裹的内容")
        return raw_content.replace('\\n', '\n').strip()  # 降级处理
    except Exception as e:
        print(f"提取失败：{str(e)}")
        return ""
    
def extract_json_from_response(chat_completion_response):
    """
    从大模型返回结果中提取并解析JSON内容
    返回: (status, data) 
        - status: True/False 表示是否成功
        - data: 解析后的字典 或 错误信息
    """
    try:
        # 获取原始文本内容
        content = chat_completion_response.choices[0].message.content
        # 方法一：正则表达式提取JSON（推荐）
        # json_str = re.search(r'```json\n(.*?)\n```', content, re.DOTALL).group(1)
        # 增强版正则：兼容有无代码块包裹的情况 ✅
        json_match = re.search(
            r'(?:```json\s*)?({.*?})(?:\s*```)?',  # 关键修改点
            content, 
            re.DOTALL
        )
        json_str = json_match.group(1)
        # 方法二：直接处理（如果确定格式固定）
        # json_str = content.split('```json\n')[1].split('\n```')[0]
        
        # 清理可能的残留符号
        json_str = json_str.strip().replace('```', '')
        
        # 解析JSON
        data = json.loads(json_str)
        return True, data
    
    except AttributeError:
        return False, "未找到JSON代码块"
    except json.JSONDecodeError as e:
        return False, f"JSON解析失败: {str(e)}"
    except Exception as e:
        return False, f"未知错误: {str(e)}"


def generate_content(question, answer_txt, template_key="rednote"):
    """使用模板生成小红书内容"""
    try:
        # 加载提示词模板
        with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
            system_prompt = f.read().format(
                topic=question['title'],
                original_text=answer_txt  # 使用从知乎获取的实际回答内容
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

    #爬取微博内容
    driver = browser.Browser()
    browser_instance = driver.start_browser()
    crawler = weibo_crawler.WeiboCrawler(driver=browser_instance)
    answer_txt, question = crawler.do()
    browser_instance.close()

    # 第一步提炼观点
    template_key = "controversy_extract"
    # 生成内容时传递完整参数
    controversy_content = generate_content(question, answer_txt, template_key)
    if not controversy_content:
        print("观点提炼失败")
        return
    # 使用示例
    status, result = extract_json_from_response(controversy_content)
    if status:
        print("提取成功！")
        print("核心争议:", result['core_controversies'])
        print("热门标签:", result['hot_tags'])
    else:
        print("错误:", result)

    # 第二步生成小红书内容
    template_key = "rednote"
    # 将争议观点从List变为字符串
    controversies_str = "\n".join([f"- {item}" for item in result['core_controversies']])
    # 加载生成提示词模版
    with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
        # 读取模板内容
        template_content = f.read()
        # 格式化提示词
        system_prompt = template_content.format(
        topic=question['title'],
        original_text=answer_txt,
        controversy_content=controversies_str  # 注意模板中要对应 {controversy_content}
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
    last_line = get_last_line(content) #取得最后一行，话题
    last_line = last_line.split('#') #把最后一行每一个话题list化
    last_line = [item for item in last_line if item] #去掉空的话题
    # print(last_line)

    #第三步，根据生成的小红书内容提取第一行小红书标题
    title = get_first_line(content)
    print('小红书标题：')
    print(title)

    #第四步根据tile生成封面图片
    # txt2img.paint_dance(desc=title, img_name='title')
    imgrender_instance = imgrender.ImgReder(txt=question['title'])
    imgrender_instance.do()
    
    # 小红书发布
    driver = browser.Browser()
    driver = driver.start_browser()
    xiaohongshu_publisher = XiaohongshuPublisher(cookie_file='cookies.pkl', image_path='/Users/ycm/Desktop/code/auto/title.png', title=title, content=content, topics_list = last_line, driver=driver)
    xiaohongshu_publisher.publish(url=config.PUBLISH_URL)


# 程序启动时检查是否需要立即执行
check_initial_schedule()
# 添加定时任务（每天12:00和18:00触发）
scheduler.add_job(
    lambda: schedule_random_job(12),
    CronTrigger(hour=12, minute=0, timezone="Asia/Shanghai")
)
scheduler.add_job(
    lambda: schedule_random_job(18),
    CronTrigger(hour=18, minute=0, timezone="Asia/Shanghai")
)

if __name__ == "__main__":
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    # job()