import http.client
import json
import config
import requests
class ImgReder():
    def __init__(self, txt, payload_chinese = False , down_path = "title.png"):
        self.payload_chinese_flag = payload_chinese
        self.conn = http.client.HTTPSConnection("api.imgrender.net")
        self.headers = config.IMGRENDER_CONFIG
        self.txt = txt 
        self.down_path = down_path
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

        self.payload_chinese = json.dumps({
        "width": 640,
        "height": 640,
        "backgroundColor": "#f5f5dc",  # 标准米色
        "lines":[
            {
                "startX": 30,
                "startY": 60,
                "endX": 610,
                "endY": 60,
                "width": 3,
                "color": "#E1E1E1",
                "zIndex": 1
            }
        ],
        "texts": [
            {
                "x": 320,  # 横向铺满
                "y": 100,  # 垂直居中位置
                "text": self.txt, #内容信息
                "font": "SourceHanSerifCN-Light",
                "fontSize": 25,
                "lineHeight": 35,  # 行高=字体大小（最紧凑排版）
                "color": "#333",
                "width": 600,  # 占满整个宽度
                "textAlign": "center",
                "zIndex": 1
            }
        ],
        "images": [
        {
            "x": 30,
            "y": 60,
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
            with open(self.down_path, "wb") as f:
                f.write(response.content)
            print("下载成功")
        else:
            print(f"下载失败，状态码：{response.status_code}")

    def do(self):
        if self.payload_chinese_flag == True:
            self.conn.request("POST", "/open/v1/pics", self.payload_chinese, self.headers)
        else:
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
    
if __name__=="__main__":
    
    # img_reder_instance = ImgReder(txt="约会视频风波震动韩娱圈  \n新曝光的居家视频显示演员金秀贤与金赛纶亲密互动，包括捶背按摩和洗碗场景。尽管经纪公司坚称'虚假消息'，赛纶家属声称掌握数千张照片视频作为证据。网友激烈争论——有人称赞'完美男友'举动，也有人质疑在赛纶离世后曝光的时机。随着鉴定专家准备对材料进行数字验证，法律战持续升级。",
    #                               payload_chinese = True, down_path = 'title1.png')
    # img_reder_instance.do()

    # imgrender_instance_png0 = ImgReder(txt='aaaaa', payload_chinese=False, down_path='title.png')
    # imgrender_instance_png0.do()

    imgrender_instance_png1 = ImgReder(txt=" kim Soo-hyun's Leaked Footage Sparks Privacy Debate! \n Newly leaked private footage shows actors Kim Soo-hyun and Kim Sae-ron casually interacting at her apartment years ago. The video captures Kim Soo-hyun patting her back when she hiccuped, washing dishes, and watching variety shows together. \n This contradicts Kim's previous denial of visiting her home, sparking heated online discussions. While some fans call it 'relationship goals' , others criticize the invasion of privacy, especially given Sae-ron's tragic passing. \n Media ethics experts warn this sets a dangerous precedent for celebrity surveillance. ", payload_chinese=True, down_path='title1.png') #生成中文翻译的图片
    imgrender_instance_png1.do()