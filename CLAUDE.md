# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

B站直播弹幕点歌机 — 监听B站直播间弹幕，通过 LX Music 桌面版的 Scheme URL 协议实现弹幕点歌/切歌功能。纯 Python 异步实现，Windows 环境运行。

## Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 启动程序
python main.py
python main.py 房间号

# 语法检查（无测试框架）
python -c "import py_compile; py_compile.compile('文件名.py', doraise=True)"
```

## Architecture

### 核心流程

```
main.py (入口)
  → bili_login.ensure_login() — 登录B站（cookie加载/刷新/扫码）
  → blivedm.BLiveClient — WebSocket连接直播间，监听弹幕
  → MyHandler._on_danmaku() — 解析弹幕指令
  → 多源搜索 (kg > wy > tx) → song_handler → LX Music 播放
```

### 模块职责

- **main.py** — 入口，弹幕事件处理，点歌/切歌逻辑
- **bili_login.py** — B站登录全流程（cookie持久化到config.json、refresh、扫码），登录后自动获取用户直播间号
- **qr_page.py** — 扫码登录时启动本地HTTP服务器(127.0.0.1:19820)，在浏览器展示二维码页面
- **lxmusic.py** — LX Music Scheme URL协议封装（文档: https://lxmusic.toside.cn/desktop/scheme-url）
- **song_handler.py** — 统一将搜索结果转为 `music/searchPlay` 调用，`playLater=True`（排队播放）
- **kg_search.py / wy_search.py / tx_search.py** — 酷狗/网易云/QQ音乐搜索模块，结构相同：`search_and_get_first(name, singer)` 返回标准化 dict 或 None
- **config.py** — 首次运行时生成 config.json
- **blivedm/** — B站直播弹幕WebSocket客户端库（第三方，不要修改）

### 搜索模块标准返回格式

每个搜索模块的 `search_and_get_first()` 返回：
```python
{
    "source": "kg" | "wy" | "tx",
    "name": str, "singer": str, "songmid": str,
    "img": str, "albumId": str, "interval": str,  # mm:ss
    "albumName": str, "types": list, "hash": str
}
```

### 配置文件 config.json

运行时自动生成，包含 `roomid` 和 `cookies`（登录凭证）。已在 .gitignore 中。

### 弹幕指令

- `点歌 歌名 [歌手]` — 点歌，歌手可选
- `下一首` — 切歌（限房管）

## Key Conventions

- 所有网络请求使用 `aiohttp`，异步处理
- 与 LX Music 通信方式：生成 Scheme URL 后通过 `webbrowser.open()` 调用
- 搜索优先级固定为 kg → wy → tx，前一个有结果就不再查后续源
- 文件编码统一 UTF-8
- 项目语言为中文（注释、提示信息、文档）
