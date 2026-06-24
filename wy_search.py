# -*- coding: utf-8 -*-
"""
网易云搜索模块 - 搜索歌曲并返回第一首的元数据，供 LX Music music/play 使用
"""
import aiohttp

WY_SEARCH_URL = "https://music.163.com/api/search/get/web"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


async def search_wy(keyword: str, page: int = 1, pagesize: int = 5) -> list:
    """
    网易云搜索歌曲
    :param keyword: 搜索关键词（歌名 + 歌手）
    :param page: 页码
    :param pagesize: 每页数量
    :return: 歌曲列表
    """
    data = {
        "s": keyword,
        "type": 1,  # 1=单曲
        "offset": (page - 1) * pagesize,
        "limit": pagesize,
    }
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://music.163.com/",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            WY_SEARCH_URL,
            data=data,
            headers=headers,
        ) as resp:
            if resp.status != 200:
                return []
            result = await resp.json(content_type=None)
            if result.get("code") != 200:
                return []
            songs = result.get("result", {}).get("songs", [])
            return songs


def parse_wy_song(song: dict) -> dict:
    """
    将网易云搜索结果转为 LX Music music/play 所需的参数格式
    """
    song_name = song.get("name", "")
    # 歌手可能是数组
    artists = song.get("artists", [])
    singer = "/".join(a.get("name", "") for a in artists) if artists else ""
    album = song.get("album", {})
    album_name = album.get("name", "") if album else ""
    album_id = album.get("id", "") if album else ""
    song_id = song.get("id", "")
    song_duration = song.get("duration", 0)  # 毫秒
    img = album.get("picUrl", "") if album else ""

    # 格式化时长 毫秒 -> mm:ss
    interval = ""
    if song_duration:
        total_seconds = song_duration // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        interval = f"{minutes:02d}:{seconds:02d}"

    # 构建 types 数组
    types = [
        {"type": "128k", "size": ""},
        {"type": "320k", "size": ""},
        {"type": "flac", "size": ""},
    ]

    return {
        "source": "wy",
        "name": song_name,
        "singer": singer,
        "songmid": str(song_id),  # wy用歌曲id作为songmid
        "img": img,
        "albumId": str(album_id) if album_id else "",
        "interval": interval,
        "albumName": album_name,
        "types": types,
        "hash": "",  # wy不需要hash
    }


async def search_and_get_first(name: str, singer: str = "") -> dict | None:
    """
    搜索网易云并返回第一首歌的 LX Music 播放参数
    :param name: 歌名
    :param singer: 歌手（可选）
    :return: music/play 所需参数 dict，失败返回 None
    """
    keyword = name
    if singer:
        keyword = f"{name} {singer}"

    try:
        songs = await search_wy(keyword)
        if not songs:
            return None
        return parse_wy_song(songs[0])
    except Exception as e:
        print(f"[搜索] 网易云搜索出错: {e}")
        return None
