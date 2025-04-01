import base64
import os.path
import config
from volcengine.visual.VisualService import VisualService
from http import HTTPStatus
from urllib.parse import urlparse, unquote
import requests
from dashscope import ImageSynthesis
import os
import config


class Txt2Img():
    def __init__(self):
        pass


    def paint_txt2img_general(self, desc, output_img_paths, prompts):
        visual_service = VisualService()
        visual_service.set_ak(config.SET_AK)
        visual_service.set_sk(config.SET_SK)
    
        # 高美感通用V2.1-文生图
        form = {
            "req_key": "high_aes_general_v21_L",
            "prompt": prompts,
            "model_version": "general_v2.1_L"
        }
    
        resp = visual_service.high_aes_smart_drawing(form)
        data = base64.b64decode(resp['data']['binary_data_base64'][0])
        with open('{}.png'.format(output_img_paths), 'wb') as f:
            f.write(data)
    
    
    def qwen_txt_to_img(self, title, output_paths):
        # prompt = "震惊！38岁群演相亲被嫌月薪3800：上综艺真能成明星？丨冯远征这话说透了！"
        template_key = "generate_img_to_toutiao"
        with open(f"prompts/{template_key}.txt", 'r', encoding='utf-8') as f:
            system_prompt = f.read().format(
                title=title,
            )

        print('----sync call, please wait a moment----')
        rsp = ImageSynthesis.call(api_key=config.QWEN_KEY,
                                model="wanx2.1-t2i-plus",
                                prompt=system_prompt,
                                n=1,
                                size='1024*1024')
        print('response: %s' % rsp)
        if rsp.status_code == HTTPStatus.OK:
            # 在当前目录下保存图片
            for result in rsp.output.results:
                file_name = output_paths+'.png'
                with open(file_name, 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('sync_call Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))
            
        
if __name__ == '__main__':
    desc = '老父亲听到孩子恋爱是什么反应？吴尊教科书式答案看哭全网！'
    # txt2img_instance = txt2img()
    # txt2img_instance.paint_dance(desc, output_img_paths, prompts)
    instance_txt2img = Txt2Img()
    instance_txt2img.qwen_txt_to_img(title = desc, output_paths = 'output_files/title1')