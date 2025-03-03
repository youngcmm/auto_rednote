import base64
import os.path
import config
from volcengine.visual.VisualService import VisualService
 
def paint_dance(desc, img_name):
    visual_service = VisualService()
    visual_service.set_ak(config.SET_AK)
    visual_service.set_sk(config.SET_SK)
 
    # 高美感通用V2.1-文生图
    form = {
        "req_key": "high_aes_general_v21_L",
        "prompt": '帮我生成可爱的手写字体，保持字体的准确，风格保持清新风格，内容如下：' + desc.strip(),
        "model_version": "general_v2.1_L"
    }
 
    resp = visual_service.high_aes_smart_drawing(form)
    data = base64.b64decode(resp['data']['binary_data_base64'][0])
    with open('{}.png'.format(img_name), 'wb') as f:
        f.write(data)
 
 
 
if __name__ == '__main__':
    desc = '高速免费新方案！车主自选天数能治堵车？'
    paint_dance(desc, img_name='title')