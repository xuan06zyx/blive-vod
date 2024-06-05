import json
import time
import requests

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
}
barrage_name = ''
barrage_list = []
barrage_text_list = []


def Get_Barrage(roomid):
    """
    获取直播间弹幕
    :param roomid: 直播间id 字符串
    :return: 弹幕列表和弹幕文本列表
    """
    while True:
        try:
            bilibili_url = f'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid={roomid}&room_type=0'
            # 获取弹幕
            bilibili = json.loads(requests.get(url=bilibili_url, headers=header).text)
            room = bilibili['data']['room']
            admin = bilibili['data']['admin']
        except requests.exceptions.ConnectionError as e:
            print(f'网络连接失败，自动重试ing...,Error:{e}')
        # 获取所有弹幕
        for i in room:
            barrage_text = i['text']  # 弹幕文本
            barrage_name = i['nickname']  # 用户名
            barrage_timeline = i['timeline']  # 发送时间
            room_barrage = f'[{barrage_timeline}] {barrage_name}: {barrage_text}'
            if room_barrage not in barrage_list:
                barrage_list.append(room_barrage)
                barrage_text_list.append(barrage_text)
                print(room_barrage)
        time.sleep(0.3)
        yield {"barrage_list": barrage_list, "barrage_text_list": barrage_text_list, "barrage_name": barrage_name}


if __name__ == '__main__':
    while True:
        Get_Barrage(24005882)
        time.sleep(0.3)  # 每隔0.3秒获取一次弹幕
