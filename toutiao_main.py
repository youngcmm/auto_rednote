from datetime import datetime
from zhihu_crawler import fetch_zhihu_hot, fetch_zhihu_hot_answer_by_jina

from xiaohongshu_publisher import XiaohongshuPublisher
from config import DEEPSEEK_CONFIG  # 简化配置导入
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import random
from datetime import datetime, timedelta
import browser
from utils.util import *
import question_decision
import toutiao_publisher
import pre_process.filtered_processed_topics
scheduler = BlockingScheduler(timezone="Asia/Shanghai")  # 设置时区
import time
time_ymd = time.strftime("%Y%m%d", time.localtime())

def job():
    # 获取知乎热榜
    hot_questions = fetch_zhihu_hot()
    if not hot_questions:
        print("未获取到热榜数据")
        return
    origin_question_list = []
    origin_answer_url_list = []
    for item in hot_questions:
        origin_question_list.append(item['title'])
        origin_answer_url_list.append(item['url'])
    
    #筛选已经发布过的内容
    new_topics_list, new_topics_answer_url_list  = pre_process.filtered_processed_topics.filter_new_topics(question_list=origin_question_list, answer_url_list=origin_answer_url_list)
    if not new_topics_list:
        print("没有新话题需要处理")
    
    #Agent筛选话题内容, Agent返回索引
    instance_zhihu_filter_toutiao = question_decision.zhihu_filter_to_toutiao(new_topics_list)
    # instance_zhihu_filter_toutiao = question_decision.zhihu_filter_to_toutiao(origin_question_list)
    filtered_index_list = instance_zhihu_filter_toutiao.filter()
    question_list = []
    answer_url_list = []
    for i in range(len(filtered_index_list)):
        question_list.append(origin_question_list[filtered_index_list[i]])
        answer_url_list.append(origin_answer_url_list[filtered_index_list[i]]) # 使用jina获取高赞回答

    #存储更新已处理的话题
    processed = pre_process.filtered_processed_topics.load_processed_topics()
    processed.update(question_list)
    pre_process.filtered_processed_topics.save_processed_topics(processed)

    #发布执行
    for i in range(len(filtered_index_list)): 
    # for i in range(1): 
        #第一步 获取知乎回答信息
        question = question_list[i]
        answer_txt = fetch_zhihu_hot_answer_by_jina(answer_url_list[i])
        
        # 第二步 提炼知乎观点
        #加载prompt模版
        template_key = "controversy_extract"
        with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
            system_prompt = f.read().format(
                topic=question,
                original_text=answer_txt  # 使用从知乎获取的实际回答内容
            )
        # 保存到新文件（避免覆盖原模板）
        output_path = f"prompts/generated_{template_key}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
        # 生成内容时传递完整参数
        controversy_content = generate_content(question=None, answer_txt=None, template_key='generated_{}'.format(template_key))
        if not controversy_content:
            print("观点提炼失败")
            return
        # 使用示例
        status, result = extract_json_from_response(controversy_content)
       # 存储观点的结果
        output_path = f"output_files/{time_ymd}/{question}/controversy.txt"
        directory = os.path.dirname(output_path)
        os.makedirs(directory, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=4))
        if status:
            print("提取成功！")
            print("核心争议:", result['core_controversies'])
            print("热门标签:", result['hot_tags'])
        else:
            print("错误:", result)

        # 第三步 生成头条内容和标题
        template_key = "toutiao"
        # 将争议观点从List变为字符串
        try:
            controversies_str = "\n".join([f"- {item}" for item in result['core_controversies']])
        except:
            print('争议观点提炼失败')
            controversies_str = ''
        # 加载生成提示词模版
        with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
            # 读取模板内容
            template_content = f.read()
            # 格式化提示词
            system_prompt = template_content.format(
            topic=question,
            original_text=answer_txt,
            controversy_content=controversies_str  # 注意模板中要对应 {controversy_content}
        )
        # 保存到新文件（避免覆盖原模板）
        output_path = f"prompts/generated_{template_key}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
        # 生成内容时传递完整参数
        response = generate_content(question=None, answer_txt=None, template_key=f'generated_{template_key}')
        if not response:
            print("内容生成失败")
            return
        
        #第四步 提取内容和标题
        respons_content = extract_post_content(response) #从大模型中返回结果提取content
                # 存储content的结果
        output_path = f"output_files/{time_ymd}/{question}/content.txt"
        directory = os.path.dirname(output_path)
        os.makedirs(directory, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(respons_content)
        
        #提取
        title, content = extract_content(respons_content)
        print('头条内容：')
        print(content)
        print('头条标题：')
        print(title)
        
        #第五步 如果标题过长进行压缩
        if len(title) > 30:
            print('标题字数大于20，正在缩减字数...')
            # 生成内容时传递完整参数
            title_short = generate_content(question=None, answer_txt=None, template_key=f'帮我缩减这个标题到20个字：{title}')
            if not title_short:
                print("内容生成失败")
                return
            title = extract_post_content(title_short) #从大模型中返回结果提取返回的标题


        #第六步 头条publish
        brow_instance = browser.Browser()
        driver = brow_instance.start_browser()
        toutiao_publish = toutiao_publisher.TouTiaoPublisher(cookie_file="cookies_toutiao.pkl", 
                                    image_path=None, 
                                    title=title, 
                                    content=content, 
                                    topics_list = result['hot_tags'], 
                                    driver = driver)
        toutiao_publish.do()
        time.sleep(5)#发布需要等待一会网络
        brow_instance.close()
        






if __name__ == "__main__":
    #     # 程序启动时检查是否需要立即执行
    # check_initial_schedule()
    # # 添加定时任务（每天12:00和18:00触发）
    # scheduler.add_job(
    #     lambda: schedule_random_job(12),
    #     CronTrigger(hour=12, minute=0, timezone="Asia/Shanghai")
    # )
    # scheduler.add_job(
    #     lambda: schedule_random_job(18),
    #     CronTrigger(hour=18, minute=0, timezone="Asia/Shanghai")
    # )
    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
    job()