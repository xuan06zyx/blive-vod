# -*- coding: utf-8 -*-
"""
QQ音乐搜索模块 - 搜索歌曲并返回第一首的元数据，供 LX Music music/play 使用
"""
import aiohttp
from search_common import USER_AGENT, build_keyword, format_interval, run_search

TX_SEARCH_URL = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"


async def search_tx(keyword: str, page: int = 1, pagesize: int = 5) -> list:
    """
    QQ音乐搜索歌曲
    :param keyword: 搜索关键词（歌名 + 歌手）
    :param page: 页码
    :param pagesize: 每页数量
    :return: 歌曲列表
    """
    params = {
        "w": keyword,
        "p": page,
        "n": pagesize,
        "format": "json",
        "cr": 1,
        "ct": 24,
        "platform": "yqq.json",
    }
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://y.qq.com/",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            TX_SEARCH_URL,
            params=params,
            headers=headers,
        ) as resp:
            if resp.status != 200:
                return []
            result = await resp.json(content_type=None)
            songs = result.get("data", {}).get("song", {}).get("list", [])
            return songs


def parse_tx_song(song: dict) -> dict:
    """
    将QQ音乐搜索结果转为 LX Music music/play 所需的参数格式
    """
    song_name = song.get("songname", "")
    # 歌手可能是数组
    singers = song.get("singer", [])
    singer = "/".join(s.get("name", "") for s in singers) if singers else ""
    album_name = song.get("albumname", "")
    album_id = song.get("albumid", "")
    songmid = song.get("songmid", "")
    str_media_mid = song.get("strMediaMid", "") or song.get("media_mid", "")
    song_duration = song.get("interval", 0)  # 秒
    # QQ音乐封面图拼接
    albummid = song.get("albummid", "")
    img = f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{albummid}.jpg" if albummid else ""

    # 格式化时长 秒 -> mm:ss
    interval = format_interval(song_duration)

    # 构建 types 数组
    size128 = song.get("size128", 0)
    size320 = song.get("size320", 0)
    size_flac = song.get("sizeflac", 0)
    types = []
    if size128:
        types.append({"type": "128k", "size": str(size128)})
    if size320:
        types.append({"type": "320k", "size": str(size320)})
    if size_flac:
        types.append({"type": "flac", "size": str(size_flac)})
    if not types:
        types.append({"type": "128k", "size": ""})

    return {
        "source": "tx",
        "name": song_name,
        "singer": singer,
        "songmid": songmid,  # tx用songmid
        "img": img,
        "albumId": str(album_id) if album_id else "",
        "interval": interval,
        "albumName": album_name,
        "types": types,
        "hash": "",  # tx不需要hash
        "strMediaMid": str_media_mid,  # tx必传
    }


async def search_and_get_first(name: str, singer: str = "") -> dict | None:
    """
    搜索QQ音乐并返回第一首歌的 LX Music 播放参数
    :param name: 歌名
    :param singer: 歌手（可选）
    :return: music/play 所需参数 dict，失败返回 None
    """
    return await run_search(search_tx, parse_tx_song, build_keyword(name, singer), "QQ音乐")
