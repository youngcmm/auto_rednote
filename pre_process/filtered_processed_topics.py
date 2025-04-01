import json
import os
import time
# 存储已处理话题的文件路径
time_ymd = time.strftime("%Y%m%d", time.localtime())
# print(time_ymd)
HISTORY_FILE = 'output_files/{}/processed_topics.json'.format(time_ymd)

def load_processed_topics():
    directory = os.path.dirname(HISTORY_FILE)
    """加载已处理的话题列表"""
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(directory, exist_ok=True) #文件不存在创建文件
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f) #存入空json
        return set()
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return set(json.load(f))

def save_processed_topics(processed_set):
    """保存已处理的话题列表"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_set), f)

def filter_new_topics(question_list, answer_url_list):
    """过滤未处理的新话题"""
    processed = load_processed_topics()
    # new_topics = [topic for topic in origin_question_list if topic not in processed]
    new_topics_list = []
    new_topics_answer_url_list = []
    for i in range(len(question_list)):
        topic = question_list[i]
        if topic not in processed: #选择之前没有发布过的话题
            new_topics_list.append(topic)
            new_topics_answer_url_list.append(answer_url_list[i]) 
    return new_topics_list, new_topics_answer_url_list

def main_workflow():
    pass
    # 第一步：爬取热榜话题
    # origin_question_list = crawl_hot_topics()  # 假设这是你的爬取函数
    origin_question_list = ['1','2']
    # 第二步：过滤未处理的话题
    new_topics, _ = filter_new_topics(origin_question_list, answer_url_list=['1','2'])
    
    # if not new_topics:
    #     print("没有新话题需要处理")
    #     return
    
    # 第三步：为每个新话题生成文本
    # for topic in new_topics:
    #     generate_text(topic)  # 假设这是你的生成函数
    
    # 第四步：更新已处理记录
    processed = load_processed_topics()
    processed.update(new_topics)
    save_processed_topics(processed)
