# -*- coding: utf-8 -*-
"""
搜索结果处理模块 - 将多源搜索结果统一转为 music/searchPlay 参数格式传给 LX Music
使用 searchPlay 方式播放，playLater=True（播放完当前歌曲后再播放点歌的歌曲）
"""
import webbrowser
import lxmusic as lxmusic_module

lxmusic = lxmusic_module.lxmusic()


def play_from_search_result(song_info: dict) -> str:
    """
    将搜索结果通过 music/searchPlay 传给 LX Music 播放
    playLater=True: 不立即播放，等当前歌曲播放完后再播放

    :param song_info: 搜索模块返回的歌曲信息 dict
        必须包含: source, name, singer
        可选包含: albumName, interval
    :return: 生成的 Scheme URL
    """
    source = song_info.get("source", "kg")
    name = song_info.get("name", "")
    singer = song_info.get("singer", "")
    album_name = song_info.get("albumName", "")
    interval = song_info.get("interval", "")

    Scheme_url = lxmusic.music_searchPlay(
        name=name,
        singer=singer,
        source=source,
        albumName=album_name,
        interval=interval,
        playLater=True,  # 播放完当前歌曲后才播放
    )
    return Scheme_url


def play_song(song_info: dict):
    """
    处理搜索结果并调用 LX Music 播放（稍后播放模式）

    :param song_info: kg_search/wy_search/tx_search 返回的歌曲信息 dict
    """
    Scheme_url = play_from_search_result(song_info)
    webbrowser.open(url=Scheme_url)
