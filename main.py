import os
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
import wy_search
import tx_search
import song_handler
from app_dir import get_config_path, get_blacklist_path

lxmusic = lxmusic.lxmusic()  # 实例化lxmusic类

session: Optional[aiohttp.ClientSession] = None


async def main(roomid):
    init_session()
    try:
        config_path = get_config_path()
        # 自动登录（加载本地cookie → 刷新 → 扫码）
        login_roomid = await bili_login.ensure_login(session)
        # 如果登录返回了直播间号且当前未配置房间号，则使用登录账号的直播间
        if login_roomid and not roomid:
            roomid = login_roomid
            print(f"[配置] 使用登录账号的直播间号: {roomid}")
            # 保存到配置文件
            try:
                with open(config_path, 'r', encoding='utf-8') as r:
                    cfg = json.load(r)
                cfg['roomid'] = roomid
                with open(config_path, 'w', encoding='utf-8') as w:
                    json.dump(cfg, w, indent=4, ensure_ascii=False)
            except Exception:
                pass
        if not roomid:
            roomid = input("请输入B站直播间号(回车确认):")
            if roomid:
                # 保存到配置文件
                try:
                    with open(config_path, 'r', encoding='utf-8') as r:
                        cfg = json.load(r)
                    cfg['roomid'] = roomid
                    with open(config_path, 'w', encoding='utf-8') as w:
                        json.dump(cfg, w, indent=4, ensure_ascii=False)
                    print(f"[配置] 房间号 {roomid} 已保存到 config.json")
                except Exception:
                    pass
        if not roomid:
            print("[错误] 未指定直播间号，程序退出")
            return
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
            # 使用异步任务多源搜索并播放（优先级: kg > wy > tx）
            asyncio.create_task(self._play_song(song_name, song_singer))

    async def _play_song(self, song_name: str, song_singer: str):
        """多源搜索获取歌曲元数据，优先级: 酷狗 > 网易云 > QQ音乐"""
        song_info = None

        # 优先级1: 酷狗搜索
        song_info = await kg_search.search_and_get_first(song_name, song_singer)
        if song_info:
            print(f'[点歌] 酷狗找到: {song_info["name"]} - {song_info["singer"]}')
        else:
            # 优先级2: 网易云搜索
            song_info = await wy_search.search_and_get_first(song_name, song_singer)
            if song_info:
                print(f'[点歌] 网易云找到: {song_info["name"]} - {song_info["singer"]}')
            else:
                # 优先级3: QQ音乐搜索
                song_info = await tx_search.search_and_get_first(song_name, song_singer)
                if song_info:
                    print(f'[点歌] QQ音乐找到: {song_info["name"]} - {song_info["singer"]}')

        if song_info:
            # 通过 song_handler 以 searchPlay 方式播放（稍后播放模式）
            song_handler.play_song(song_info)
        else:
            # 所有源都搜索失败，回退到 searchPlay
            print(f'[点歌] 所有源均无结果，使用默认搜索')
            Scheme_url = lxmusic.music_searchPlay(name=song_name, singer=song_singer, playLater=True)
            webbrowser.open(url=Scheme_url)


if __name__ == '__main__':

    import config
    config.create_config()  # 创建配置文件

    # 打开配置文件
    with open(get_config_path(), 'r', encoding='utf-8') as r:
        data = json.load(r)

    # 获取命令行参数
    roomid = ""
    if len(sys.argv) > 1:
        roomid = sys.argv[1]  # 位置为1的参数 0是本程序
    elif data['roomid'] != '':
        roomid = data['roomid']  # 配置文件中存在roomid则使用配置文件中的roomid

    BlackSong_list = []  # 定义一个空列表用于存储屏蔽词
    # 打开黑名单文件并读取内容
    blacklist_path = get_blacklist_path()
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r', encoding='utf-8') as Blacklist:
            Blacklist_lines = Blacklist.readlines()
        for line in Blacklist_lines:
            BlackSong = line.strip()
            BlackSong_list.append(BlackSong)

    # 实例化BLiveClient
    asyncio.run(main(roomid))
