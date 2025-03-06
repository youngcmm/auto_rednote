import http.client
import json
import config
import requests
class ImgReder():
    def __init__(self, txt):
        self.conn = http.client.HTTPSConnection("api.imgrender.net")
        self.headers = config.IMGRENDER_CONFIG
        self.txt = txt 
        self.payload = json.dumps({
            "width": 640,
            "height": 640,
            "backgroundColor": "#f5f5dc",  # 标准米色
            "lines":[
                {
                    "startX": 30,
                    "startY": 100,
                    "endX": 610,
                    "endY": 100,
                    "width": 3,
                    "color": "#E1E1E1",
                    "zIndex": 1
                }
            ],
            "texts": [
                {
                    "x": 320,  # 横向铺满
                    "y": 320,  # 垂直居中位置
                    "text": self.txt+'...', #内容信息
                    "font": "jiangxizhuokai",
                    "fontSize": 36,
                    "lineHeight": 36,  # 行高=字体大小（最紧凑排版）
                    "color": "#333",
                    "width": 640,  # 占满整个宽度
                    "textAlign": "center",
                    "zIndex": 1
                }
            ],
            "images": [
            {
                "x": 30,
                "y": 100,
                "width": 30,
                "height": 30,
                "url": "https://img0.baidu.com/it/u=3873463067,3391127433&fm=253&fmt=auto&app=138&f=JPEG?w=260&h=274",
                "borderRadius": 60,
                "zIndex": 1
            },]
        })
    
    def down_img(self, url):
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            with open("title.png", "wb") as f:
                f.write(response.content)
            print("下载成功")
        else:
            print(f"下载失败，状态码：{response.status_code}")

    def do(self):
        self.conn.request("POST", "/open/v1/pics", self.payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        result = data.decode("utf-8")
        try:
            json_data = json.loads(result)
            print("转换成功:")
            print(json_data)
            
            # 提取URL示例
            image_url = json_data['data']['url']
            print("\n提取到的图片地址:", image_url)

        except json.JSONDecodeError as e:
            print("JSON解析失败:", e)
        except KeyError as e:
            print("键不存在:", e)

        self.down_img(image_url)
        return True 
    

# img_reder_instance = ImgReder(txt='你好')
# img_reder_instance.do()