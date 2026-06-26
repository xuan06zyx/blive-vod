# -*- coding: utf-8 -*-
"""
B站登录模块 - Cookie持久化 + 自动刷新 + 扫码登录
避免频繁重新登录导致的人脸验证
"""
import os
import json
import time
import hashlib
import asyncio
import webbrowser
from typing import Optional, Tuple

import aiohttp
from app_dir import get_config_path

CONFIG_FILE = get_config_path()

# B站登录相关API
NAV_URL = "https://api.bilibili.com/x/web-interface/nav"
QR_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
QR_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
REFRESH_COOKIE_URL = "https://passport.bilibili.com/x/passport-login/web/cookie/refresh"
CONFIRM_REFRESH_URL = "https://passport.bilibili.com/x/passport-login/web/confirm/refresh"
COOKIE_INFO_URL = "https://passport.bilibili.com/x/passport-login/web/cookie/info"
LIVE_ROOM_URL = "https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

async def check_cookie_valid(session: aiohttp.ClientSession) -> bool:
    """检查当前session中的cookie是否有效"""
    try:
        async with session.get(NAV_URL, headers={"User-Agent": USER_AGENT}) as resp:
            data = await resp.json()
            if data["code"] == 0 and data["data"].get("isLogin"):
                uname = data["data"].get("uname", "未知")
                print(f"[登录] 当前登录用户: {uname}")
                return True
    except Exception as e:
        print(f"[登录] 检查cookie时出错: {e}")
    return False


async def get_user_info(session: aiohttp.ClientSession) -> Optional[dict]:
    """获取当前登录用户的信息（昵称、UID）"""
    try:
        async with session.get(NAV_URL, headers={"User-Agent": USER_AGENT}) as resp:
            data = await resp.json()
            if data["code"] == 0 and data["data"].get("isLogin"):
                return {
                    "uname": data["data"].get("uname", "未知"),
                    "uid": data["data"].get("mid", 0),
                }
    except Exception:
        pass
    return None


async def get_user_live_room(session: aiohttp.ClientSession, uid: int) -> Optional[str]:
    """通过UID获取用户的直播间号"""
    try:
        params = {"mid": uid}
        async with session.get(
            LIVE_ROOM_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
        ) as resp:
            data = await resp.json()
            if data["code"] == 0:
                roomid = data["data"].get("roomid", 0)
                if roomid:
                    return str(roomid)
    except Exception:
        pass
    return None


async def check_need_refresh(session: aiohttp.ClientSession) -> bool:
    """检查cookie是否需要刷新（接近过期）"""
    try:
        async with session.get(
            COOKIE_INFO_URL,
            headers={"User-Agent": USER_AGENT},
        ) as resp:
            data = await resp.json()
            if data["code"] == 0:
                refresh = data["data"].get("refresh", False)
                return refresh  # True表示需要刷新
    except Exception:
        pass
    return False


def _get_correspond_path(timestamp: int) -> str:
    """生成refresh用的correspond_path（简化版，使用公钥加密时间戳）"""
    # B站的correspond_path实际是用RSA公钥加密timestamp
    # 这里用简化实现：直接用md5 hash
    # 注意：如果B站严格校验，可能需要完整RSA实现
    return hashlib.md5(f"refresh_{timestamp}".encode()).hexdigest()


async def refresh_cookie(session: aiohttp.ClientSession, refresh_token: str, bili_jct: str) -> Optional[dict]:
    """
    使用refresh_token刷新cookie
    返回新的cookie信息dict，失败返回None
    """
    timestamp = int(time.time() * 1000)
    correspond_path = _get_correspond_path(timestamp)

    try:
        async with session.post(
            REFRESH_COOKIE_URL,
            headers={"User-Agent": USER_AGENT},
            data={
                "csrf": bili_jct,
                "refresh_csrf": correspond_path,
                "source": "main_web",
                "refresh_token": refresh_token,
            },
        ) as resp:
            data = await resp.json()
            if data["code"] == 0:
                result = data["data"]
                new_refresh_token = result.get("refresh_token", "")
                # 从响应的Set-Cookie中获取新的cookie值
                new_cookies = {}
                for cookie in resp.cookies.values():
                    if cookie.key in ("SESSDATA", "bili_jct", "DedeUserID"):
                        new_cookies[cookie.key] = cookie.value

                if new_cookies.get("SESSDATA") and new_refresh_token:
                    # 确认刷新（使旧refresh_token失效）
                    await _confirm_refresh(
                        session, new_cookies.get("bili_jct", bili_jct), refresh_token
                    )
                    print("[登录] Cookie刷新成功!")
                    return {
                        "sessdata": new_cookies["SESSDATA"],
                        "bili_jct": new_cookies.get("bili_jct", bili_jct),
                        "dedeuserid": new_cookies.get("DedeUserID", ""),
                        "refresh_token": new_refresh_token,
                    }
            else:
                print(f"[登录] 刷新cookie失败: {data.get('message', '未知错误')}")
    except Exception as e:
        print(f"[登录] 刷新cookie时出错: {e}")
    return None


async def _confirm_refresh(session: aiohttp.ClientSession, csrf: str, old_refresh_token: str):
    """确认刷新，使旧的refresh_token失效"""
    try:
        await session.post(
            CONFIRM_REFRESH_URL,
            headers={"User-Agent": USER_AGENT},
            data={
                "csrf": csrf,
                "refresh_token": old_refresh_token,
            },
        )
    except Exception:
        pass


def save_cookies(sessdata: str, bili_jct: str, dedeuserid: str, refresh_token: str):
    """保存cookie和refresh_token到config.json"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    config["cookies"] = {
        "sessdata": sessdata,
        "bili_jct": bili_jct,
        "dedeuserid": dedeuserid,
        "refresh_token": refresh_token,
        "save_time": int(time.time()),
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("[登录] Cookie已保存到 config.json")


def load_cookies() -> Optional[dict]:
    """从config.json加载cookie"""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        cookie_data = config.get("cookies")
        if cookie_data and "sessdata" in cookie_data and "refresh_token" in cookie_data:
            return cookie_data
    except (json.JSONDecodeError, KeyError):
        pass
    return None


async def qr_login(session: aiohttp.ClientSession) -> Optional[dict]:
    """
    扫码登录流程
    返回cookie信息dict，失败返回None
    """
    # 1. 获取二维码
    try:
        async with session.get(
            QR_GENERATE_URL, headers={"User-Agent": USER_AGENT}
        ) as resp:
            data = await resp.json()
            if data["code"] != 0:
                print(f"[登录] 获取二维码失败: {data.get('message')}")
                return None
            qr_url = data["data"]["url"]
            qrcode_key = data["data"]["qrcode_key"]
    except Exception as e:
        print(f"[登录] 获取二维码出错: {e}")
        return None

    # 2. 使用浏览器展示二维码页面
    import qr_page
    qr_page.show_qr_page(qr_url)

    # 3. 轮询扫码状态
    print("[登录] 等待扫码...", end="", flush=True)
    for _ in range(180):  # 最多等3分钟
        await asyncio.sleep(2)
        try:
            async with session.get(
                QR_POLL_URL,
                params={"qrcode_key": qrcode_key},
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                poll_data = await resp.json()
                status_code = poll_data["data"]["code"]

                if status_code == 0:
                    # 登录成功
                    print("\n[登录] 扫码登录成功!")
                    qr_page.close_qr_page()
                    refresh_token = poll_data["data"].get("refresh_token", "")
                    # 从响应cookie中提取
                    cookies = {}
                    for cookie in resp.cookies.values():
                        if cookie.key in ("SESSDATA", "bili_jct", "DedeUserID"):
                            cookies[cookie.key] = cookie.value
                    # 也从session的cookie_jar中获取
                    import yarl
                    jar_cookies = session.cookie_jar.filter_cookies(
                        yarl.URL("https://bilibili.com")
                    )
                    for key in ("SESSDATA", "bili_jct", "DedeUserID"):
                        if key not in cookies and key in jar_cookies:
                            cookies[key] = jar_cookies[key].value

                    if cookies.get("SESSDATA"):
                        return {
                            "sessdata": cookies["SESSDATA"],
                            "bili_jct": cookies.get("bili_jct", ""),
                            "dedeuserid": cookies.get("DedeUserID", ""),
                            "refresh_token": refresh_token,
                        }
                    else:
                        print("[登录] 登录成功但未获取到SESSDATA")
                        return None

                elif status_code == 86038:
                    print("\n[登录] 二维码已过期，请重新操作")
                    qr_page.close_qr_page()
                    return None
                elif status_code == 86090:
                    print("\r[登录] 已扫码，请在手机上确认...", end="", flush=True)
                # 86101 = 未扫码，继续等待

        except Exception as e:
            print(f"\n[登录] 轮询出错: {e}")
            qr_page.close_qr_page()
            return None

    print("\n[登录] 等待超时")
    qr_page.close_qr_page()
    return None


def apply_cookies_to_session(session: aiohttp.ClientSession, cookie_data: dict):
    """将cookie数据应用到aiohttp session"""
    import http.cookies
    cookies = http.cookies.SimpleCookie()
    cookies["SESSDATA"] = cookie_data["sessdata"]
    cookies["SESSDATA"]["domain"] = "bilibili.com"
    if cookie_data.get("bili_jct"):
        cookies["bili_jct"] = cookie_data["bili_jct"]
        cookies["bili_jct"]["domain"] = "bilibili.com"
    if cookie_data.get("dedeuserid"):
        cookies["DedeUserID"] = cookie_data["dedeuserid"]
        cookies["DedeUserID"]["domain"] = "bilibili.com"
    session.cookie_jar.update_cookies(cookies)


async def _confirm_account_and_get_room(session: aiohttp.ClientSession) -> Tuple[bool, Optional[str]]:
    """
    询问用户是否使用当前已登录账号，并在确认后获取其直播间号。

    返回 (accepted, roomid):
    - accepted=True  表示使用该账号（roomid 为其直播间号，可能为 None）
    - accepted=False 表示用户拒绝，需要切换账号扫码登录
    """
    user_info = await get_user_info(session)
    if not user_info:
        # 获取用户信息失败（如网络抖动），但cookie本身有效，继续使用该账号
        print("[登录] 未能获取账号详情，但Cookie有效，继续使用")
        return True, None

    uname = user_info["uname"]
    uid = user_info["uid"]
    choice = input(f"[登录] 检测到账号: {uname} (UID:{uid})，是否使用该账号？(y/n): ").strip().lower()
    if choice in ('y', 'yes', ''):
        roomid = await get_user_live_room(session, uid)
        if roomid:
            print(f"[登录] 已获取 {uname} 的直播间号: {roomid}")
        return True, roomid

    # 用户选择不使用该账号，清除cookie，走扫码登录
    print("[登录] 切换账号，准备扫码登录...")
    session.cookie_jar.clear()
    return False, None


async def ensure_login(session: aiohttp.ClientSession) -> Optional[str]:
    """
    确保已登录的主入口。优先级：
    1. 从本地文件加载cookie → 验证有效性 → 询问用户是否使用该账号
    2. 如果快过期 → 尝试refresh
    3. 如果无效/无本地cookie/用户拒绝 → 扫码登录

    返回登录账号的直播间号（如有），否则返回None
    """
    # 第一步：尝试从文件加载
    cookie_data = load_cookies()
    if cookie_data:
        print("[登录] 从本地加载已保存的Cookie...")
        apply_cookies_to_session(session, cookie_data)

        # 检查是否有效
        if await check_cookie_valid(session):
            # 检查是否需要刷新cookie
            if await check_need_refresh(session):
                print("[登录] Cookie即将过期，尝试自动刷新...")
                new_data = await refresh_cookie(
                    session,
                    cookie_data["refresh_token"],
                    cookie_data.get("bili_jct", ""),
                )
                if new_data:
                    save_cookies(
                        new_data["sessdata"],
                        new_data["bili_jct"],
                        new_data["dedeuserid"],
                        new_data["refresh_token"],
                    )
                    apply_cookies_to_session(session, new_data)
                else:
                    print("[登录] 刷新失败，当前Cookie仍可用，继续使用")
            accepted, roomid = await _confirm_account_and_get_room(session)
            if accepted:
                return roomid
            # 用户拒绝 → 落到扫码登录
        else:
            # Cookie无效，尝试refresh
            print("[登录] Cookie已失效，尝试使用refresh_token刷新...")
            new_data = await refresh_cookie(
                session,
                cookie_data["refresh_token"],
                cookie_data.get("bili_jct", ""),
            )
            if new_data:
                save_cookies(
                    new_data["sessdata"],
                    new_data["bili_jct"],
                    new_data["dedeuserid"],
                    new_data["refresh_token"],
                )
                apply_cookies_to_session(session, new_data)
                if await check_cookie_valid(session):
                    accepted, roomid = await _confirm_account_and_get_room(session)
                    if accepted:
                        return roomid
                    # 用户拒绝 → 落到扫码登录

    # 第二步：需要扫码登录
    print("[登录] 需要扫码登录...")
    login_result = await qr_login(session)
    if login_result:
        save_cookies(
            login_result["sessdata"],
            login_result["bili_jct"],
            login_result["dedeuserid"],
            login_result["refresh_token"],
        )
        apply_cookies_to_session(session, login_result)
        # 登录成功后获取用户直播间
        user_info = await get_user_info(session)
        if user_info:
            roomid = await get_user_live_room(session, user_info["uid"])
            if roomid:
                print(f"[登录] 已获取 {user_info['uname']} 的直播间号: {roomid}")
            return roomid
        return None

    print("[登录] 登录失败，将以未登录状态运行（弹幕用户名会打码）")
    return None
