from main import generate_content
from zhihu_crawler import fetch_zhihu_hot
import json
import utils.util
import re

class zhihu_filter_to_toutiao():
    def __init__(self, questions_list):
        self.questions_list = questions_list
        # self.answer_url_list = []
        self.choose_list = []

    def filter(self):
        # self.hot_questions = fetch_zhihu_hot()
        # for item in self.hot_questions:
            # self.questions_list.append(item['title'])
            # self.answer_url_list.append(item['url'])

        # 将列表转换为JSON格式字符串，保留中文和特殊符号
        self.questions_json = json.dumps(self.questions_list, ensure_ascii=False, indent=2)
        with open(f"prompts/question_decision_to_toutiao.txt", 'r', encoding='utf-8') as f:
            system_prompt = f.read().format(
                questions_list = self.questions_list #这里是判断筛选主题的任务的提示词，替换掉提示词中的内容
            )
        # 保存到新文件（避免覆盖原模板）
        output_path = f"prompts/generated_question_decision_to_toutiao.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)

        output = generate_content(question=self.questions_list, answer_txt=None, template_key='generated_question_decision_to_toutiao') #使用大模型筛选需要从知乎搬运到头条的内容，返回索引list
        content = utils.util.extract_post_content(output)
        match = re.search(r"\[.*?\]", content)
        if match:
            self.choose_list = eval(match.group())  # 用 eval 解析字符串为 list
            # print(choose_list)  # 输出: [1, 6, 21]
        return self.choose_list