import json
import re
from config import *
from openai import OpenAI
import ast
client = OpenAI(
    api_key=DEEPSEEK_CONFIG["api_key"],
    base_url=DEEPSEEK_CONFIG["base_url"]
)
from bs4 import BeautifulSoup

def save_content(content, path):
    answer_txt_path = path
    directory = os.path.dirname(answer_txt_path)
    os.makedirs(directory, exist_ok=True)
    with open(answer_txt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def extract_weibo_comments(html_str):
    """
    从微博HTML内容中提取所有用户的留言文本
    :param html_str: 网页HTML字符串
    :return: 留言文本列表
    """
    soup = BeautifulSoup(html_str, 'html.parser')
    comments = []
    
    # 查找所有包含留言的div元素
    for weibo_text in soup.find_all('div', class_='weibo-text'):
        # 提取文本内容并清理格式
        text = weibo_text.get_text(' ', strip=True)
        # 合并多个连续空格
        text = ' '.join(text.split())
        if text:
            comments.append(text)
    
    return comments

def get_last_line(s):
    lines = s.splitlines()
    return lines[-1] if lines else ''

def get_first_line(s):
    lines = s.splitlines()
    return lines[0] if lines else ''

def extract_title(text):
    # 尝试匹配 "标题：{这里是标题内容}" 的形式
    bracket_match = re.search(r'标题：\s*{(.*?)}', text)
    if bracket_match:
        return bracket_match.group(1)
    
    # 处理 "标题：这里是标题内容：这里也是标题内容" 的形式
    colon_split = re.split(r'标题：\s*', text, 1)  # 按中文冒号分割
    if len(colon_split) >= 2:
        return colon_split[1].strip()  # 提取分割后的内容并去除首尾空格
    
    return text  # 默认返回原标题

def extract_content(text):
    # 按换行符分割文本块
    blocks = text.strip().split('\n')
    
    # 提取标题（首行内容）
    try:
        title = blocks[0].split(':",')[0] + '"'  # 修复标题引号闭合
    except:
        title = blocks
    # 提取内容模块（去除首行后的所有行）
    content = '\n'.join([line.strip() for line in blocks[1:] if line.strip()])
    
    return title, content

def extract_fields_toutiao(chat_completion_response):
    content = chat_completion_response.choices[0].message.content

    # content = chat_completion_response
    try:
        # 增强版正则：兼容有无代码块包裹的情况 ✅
        json_match = re.search(
            r'(?:```json\s*)?({.*?})(?:\s*```)?',  # 关键修改点
            content, 
            re.DOTALL
        )
        json_str = json_match.group(1)
        # 清理可能的残留符号
        json_str = json_str.strip().replace('```', '')
        
        # 解析JSON数据
        data = json.loads(json_str)

        # 提取目标字段
        return {
            "title": data.get("title", ""),
            "content": data.get("content", "")
        }
    except json.JSONDecodeError:
        print("错误：无效的JSON格式")
        return content


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
    

def convert_text_to_html(text):
    """ 将纯文本转换为基本HTML格式
    功能：
    1. 处理换行符 -> 转为 <p> 段落
    2. 保留特殊符号（如🔥）
    3. 防止XSS攻击转义
    """
    # 分割段落并包裹<p>标签
    paragraphs = [
        f"<p>{line}</p>" for line in text.split('\n') 
        # if line.strip() != ''  # 过滤空行
    ]
    
    # 组合成完整HTML（带默认字体设置）
    return f"""
        {''.join(paragraphs)}
    """


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
            try:
                with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except:
                system_prompt = template_key

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

def extract_fields_json(json_str):
    try:
        # 预处理：将实际换行符转义为JSON可识别的\n
        processed_str = json_str.replace('\n', '\\n')
        # 解析JSON字符串
        data = json.loads(processed_str)
        
        # 提取字段并设置默认值
        return {
            "title": data.get("title", ""),
            "content": data.get("content", "").replace('\n', ' ')  # 将换行符转为空格
        }
    except json.JSONDecodeError:
        print("错误：无效的JSON格式")
        return json_str
    
    
# txt = _convert_text_to_html(text='🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？\n 🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？')
# print(txt)

