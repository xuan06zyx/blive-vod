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
import bili_login
import kg_search

lxmusic = lxmusic.lxmusic()  # 实例化lxmusic类

currentVersion = 2.03

session: Optional[aiohttp.ClientSession] = None


async def main(roomid):
    init_session()
    try:
        # 自动登录（加载本地cookie → 刷新 → 扫码）
        await bili_login.ensure_login(session)
        print(f"[信息] 监听房间号: {roomid}  https://live.bilibili.com/{roomid}")
        await run_single_client(room_id=int(roomid))
    finally:
        await session.close()


def init_session():
    global session
    session = aiohttp.ClientSession()


async def run_single_client(room_id: int):
    """
    监听一个直播间
    """
    room_id = room_id
    client = blivedm.BLiveClient(room_id, session=session)
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
                return
            print(f'收到点歌请求: {song_name} 歌手:{song_singer}')
            # 使用异步任务搜索酷狗并精确播放
            asyncio.create_task(self._play_song(song_name, song_singer))

    async def _play_song(self, song_name: str, song_singer: str):
        """搜索酷狗获取第一首歌的元数据，通过 music/play 精确播放"""
        song_info = await kg_search.search_and_get_first(song_name, song_singer)
        if song_info:
            print(f'[点歌] 找到: {song_info["name"]} - {song_info["singer"]}')
            Scheme_url = lxmusic.music_play(
                source=song_info["source"],
                name=song_info["name"],
                singer=song_info["singer"],
                songmid=song_info["songmid"],
                img=song_info["img"],
                albumId=song_info["albumId"],
                interval=song_info["interval"],
                albumName=song_info["albumName"],
                types=song_info["types"],
                hash=song_info["hash"],
            )
            webbrowser.open(url=Scheme_url)
        else:
            # 搜索失败，回退到 searchPlay
            print(f'[点歌] 酷狗搜索无结果，使用默认搜索')
            Scheme_url = lxmusic.music_searchPlay(name=song_name, singer=song_singer, playLater=True)
            webbrowser.open(url=Scheme_url)


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
        # 保存房间号到配置文件
        if roomid:
            data['roomid'] = roomid
            with open('config.json', 'w', encoding='utf-8') as w:
                json.dump(data, w, indent=4, ensure_ascii=False)
            print(f"[配置] 房间号 {roomid} 已保存到 config.json")

    BlackSong_list = []  # 定义一个空列表用于存储屏蔽词
    # 打开黑名单文件并读取内容
    with open('.A歌曲黑名单.txt', 'r', encoding='utf-8') as Blacklist:  # utf-8编码
        Blacklist_lines = Blacklist.readlines()  # 读取所有行
    for line in Blacklist_lines:
        BlackSong = line.strip()  # 去除行末的换行符和多余的空格
        BlackSong_list.append(BlackSong)  # 添加到列表

    # 实例化BLiveClient
    asyncio.run(main(roomid))
