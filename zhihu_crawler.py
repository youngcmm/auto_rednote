import requests
from bs4 import BeautifulSoup
import json
import config
def fetch_zhihu_hot():
    #利用https://www.zhihu.com/billboard直接解析热榜数据得到
    """
    return = 
    [{
    'title':'', 热榜标题
    'excerpt':'', 热榜摘要
    'heat':'', #热榜指数
    'url':'', 地址
    },
    {}]
    """
    """获取知乎热榜数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 请求热榜页面
        response = requests.get('https://www.zhihu.com/billboard', headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析初始数据
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', id='js-initialData')
        
        if script_tag:
            # 解析JSON数据
            init_data = json.loads(script_tag.string)
            # 修正数据解析路径
            hot_list = init_data.get('initialState', {}).get('topstory', {}).get('hotList', [])
            
            # 提取结构化数据
            result = []
            for item in hot_list:
                target = item.get('target', {})
                # 修正字段获取路径
                title_area = target.get('titleArea', {})
                excerpt_area = target.get('excerptArea', {})
                metrics_area = target.get('metricsArea', {})
                link = target.get('link', {}).get('url', '')
                
                # 智能处理URL拼接
                final_url = link if link.startswith('http') else f"https://www.zhihu.com{link}"
                
                hot_item = {
                    'title': title_area.get('text', ''),  # 从titleArea获取带格式的标题
                    'excerpt': excerpt_area.get('text', ''),  # 从excerptArea获取摘要
                    'heat': metrics_area.get('text', '').replace('热度', '').strip(),
                    'url': final_url
                }
                result.append(hot_item)
            
            return result
        return []

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return []
    except json.JSONDecodeError:
        print("JSON解析失败")
        return []

def fetch_zhihu_hot_answer_by_jina(url_input):
    #调用jina获取
    config_key = config.JINA_CONFIG['api_key']
    url = f'https://r.jina.ai/{url_input}'
    headers = {
    'Authorization': 'Bearer {}'.format(config_key)
    } #jina的key
    response = requests.get(url, headers=headers)
    # print(response.text)
    return response.text

# hot_list = fetch_zhihu_hot()
# print(fetch_zhihu_hot_answer_by_jina(hot_list[0]['url']))