# -*- coding: utf-8 -*-
"""
搜索模块公共工具 - 各音源搜索模块（kg/wy/tx）共享的常量与辅助函数
"""

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def build_keyword(name: str, singer: str = "") -> str:
    """拼接搜索关键词（歌名 + 歌手）"""
    return f"{name} {singer}" if singer else name


def format_interval(seconds: int) -> str:
    """将秒数格式化为 mm:ss，无效时长返回空串"""
    if not seconds:
        return ""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


async def run_search(search_fn, parser, keyword: str, source_label: str):
    """
    统一执行搜索：调用 search_fn 拿列表，取第一首交给 parser 解析。
    失败或无结果返回 None。
    :param search_fn: async 搜索函数，接收 keyword，返回歌曲列表
    :param parser: 解析函数，接收单首歌 dict，返回标准化 dict
    :param keyword: 搜索关键词
    :param source_label: 出错日志中显示的音源名称（如 "酷狗"）
    """
    try:
        songs = await search_fn(keyword)
        if not songs:
            return None
        return parser(songs[0])
    except Exception as e:
        print(f"[搜索] {source_label}搜索出错: {e}")
        return None
