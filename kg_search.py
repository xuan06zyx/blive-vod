# -*- coding: utf-8 -*-
"""
酷狗搜索模块 - 搜索歌曲并返回第一首的元数据，供 LX Music music/play 使用
"""
import aiohttp

KG_SEARCH_URL = "http://mobilecdn.kugou.com/api/v3/search/song"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


async def search_kg(keyword: str, page: int = 1, pagesize: int = 5) -> list:
    """
    酷狗搜索歌曲
    :param keyword: 搜索关键词（歌名 + 歌手）
    :param page: 页码
    :param pagesize: 每页数量
    :return: 歌曲列表
    """
    params = {
        "format": "json",
        "keyword": keyword,
        "page": page,
        "pagesize": pagesize,
        "showtype": 1,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            KG_SEARCH_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            songs = data.get("data", {}).get("info", [])
            return songs


def parse_kg_song(song: dict) -> dict:
    """
    将酷狗搜索结果转为 LX Music music/play 所需的参数格式
    """
    # 酷狗返回的字段
    song_name = song.get("songname", "")
    singer = song.get("singername", "")
    album_name = song.get("album_name", "")
    album_id = song.get("album_id", "")
    hash_value = song.get("hash", "")  # kg源必须
    hash_320 = song.get("320hash", "")
    hash_flac = song.get("sqhash", "")  # 无损
    song_duration = song.get("duration", 0)
    img = song.get("imgUrl", "") or song.get("img", "")

    # 格式化时长 秒 -> mm:ss
    interval = ""
    if song_duration:
        minutes = song_duration // 60
        seconds = song_duration % 60
        interval = f"{minutes:02d}:{seconds:02d}"

    # 构建 types 数组
    types = []
    if hash_value:
        types.append({"type": "128k", "size": "", "hash": hash_value})
    if hash_320:
        types.append({"type": "320k", "size": "", "hash": hash_320})
    if hash_flac:
        types.append({"type": "flac", "size": "", "hash": hash_flac})
    if not types:
        types.append({"type": "128k", "size": "", "hash": hash_value})

    return {
        "source": "kg",
        "name": song_name,
        "singer": singer,
        "songmid": hash_value,  # kg用hash作为songmid
        "img": img,
        "albumId": str(album_id) if album_id else "",
        "interval": interval,
        "albumName": album_name,
        "types": types,
        "hash": hash_value,
    }


async def search_and_get_first(name: str, singer: str = "") -> dict | None:
    """
    搜索酷狗并返回第一首歌的 LX Music 播放参数
    :param name: 歌名
    :param singer: 歌手（可选）
    :return: music/play 所需参数 dict，失败返回 None
    """
    keyword = name
    if singer:
        keyword = f"{name} {singer}"

    try:
        songs = await search_kg(keyword)
        if not songs:
            return None
        return parse_kg_song(songs[0])
    except Exception as e:
        print(f"[搜索] 酷狗搜索出错: {e}")
        return None
