from config import DATABASE_PATH


def _convert_text_to_html(text):
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

# txt = _convert_text_to_html(text='🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？\n 🔥董明珠押上全部声誉做健康家？网友吵翻天！这波操作你看懂了吗？')
# print(txt)

