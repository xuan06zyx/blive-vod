import re
import sys
import json
import aiohttp
import asyncio
import webbrowser
import http.cookies
from typing import *

import lxmusic
import blivedm
import blivedm.models.web as web_models

lxmusic = lxmusic.lxmusic()  # 实例化lxmusic类

currentVersion = 2.02

# 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
SESSDATA = ''

session: Optional[aiohttp.ClientSession] = None


async def main(roomid):
    init_session()
    try:
        await run_single_client(room_id=int(roomid))
    finally:
        await session.close()


def init_session():
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = SESSDATA
    cookies['SESSDATA']['domain'] = 'bilibili.com'

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client(room_id: int):
    """
    监听一个直播间
    """
    room_id = room_id
    client = blivedm.BLiveClient(room_id)
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        msg = message.msg  # 弹幕内容
        uname = message.uname  # 用户名
        admin = message.admin  # 是否房管 0:否 1:是
        print(f'[{message.timestamp}] {uname}：{msg}')

        # 弹幕切歌
        if msg == '下一首' and admin == 1:  # 限房管
            webbrowser.open(lxmusic.player_skipNext())  # 切换下一首

        # 弹幕点歌
        diange = re.match(r'点歌\s+(\S+)(?:\s+(\S+))?', msg)
        if diange:
            song_name = diange.group(1)  # 匹配的歌名
            song_singer = diange.group(2) if diange.group(2) else ""  # 匹配的歌手 如果没有指定则为空

            # 判断屏蔽词
            if song_name in BlackSong_list:
                print(f'发现屏蔽词:{song_name},发送者:{uname}')
            print(f'收到点歌请求: {song_name} 歌手:{song_singer}')
            Scheme_url = lxmusic.music_searchPlay(name=song_name, singer=song_singer, playLater=True)  # True表示不立即播放
            webbrowser.open(url=Scheme_url)  # 使用webbrowser打开Scheme URL


if __name__ == '__main__':

    import config
    import version
    config.create_config(currentVersion)  # 创建配置文件

    # 打开配置文件
    with open('config.json', 'r', encoding='utf-8') as r:
        data = json.load(r)

    version.version(currentVersion, data['release_api'])  # 调用版本检查方法

    # 获取命令行参数
    if len(sys.argv) > 1:
        roomid = sys.argv[1]  # 位置为1的参数 0是本程序
    elif data['roomid'] != '':
        roomid = data['roomid']  # 配置文件中存在roomid则使用配置文件中的roomid
    else:
        roomid = input("请输入B站直播间号(回车确认):")  # 没有则执行手动输入

    BlackSong_list = []  # 定义一个空列表用于存储屏蔽词
    # 打开黑名单文件并读取内容
    with open('.A歌曲黑名单.txt', 'r', encoding='utf-8') as Blacklist:  # utf-8编码
        Blacklist_lines = Blacklist.readlines()  # 读取所有行
    for line in Blacklist_lines:
        BlackSong = line.strip()  # 去除行末的换行符和多余的空格
        BlackSong_list.append(BlackSong)  # 添加到列表

    # 实例化BLiveClient
    asyncio.run(main(roomid))
