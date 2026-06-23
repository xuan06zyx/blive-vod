<div align="center">

<h1>Blive-Vod</h1>
<h1>阿B直播弹幕点歌机</h1>

</div>

*****本程序由纯Python制作而成，项目还在开发测试中极度不成熟，推荐有一定代码基础的用户使用本软件*****
## 免责声明

本软件仅供学习交流使用，请于下载后24小时内删除，不得用于任何商业用途，否则后果自负。

## 功能特性

- [x] 实时监控直播间弹幕
- [x] 弹幕点歌（支持指定歌手）
- [x] 弹幕切歌（房管权限）
- [x] 歌曲黑名单过滤
- [x] **B站自动登录**（扫码登录 + Cookie持久化 + 自动刷新）
- [x] **酷狗音乐精确搜索**（获取完整歌曲元数据，避免搜索偏差）
- [x] **房间号记忆**（首次输入后自动保存）
- [x] 异步点歌处理（不阻塞弹幕监听）
- [ ] 前端展示歌单
- [ ] 制作UI

## 快速开始

### 环境要求
- Windows 10/11 x64
- Python 3.9+ ([下载地址](https://www.python.org/downloads/windows/))
- [落雪音乐桌面版](https://github.com/lyswhut/lx-music-desktop/releases) 2.8.0+

### 安装步骤

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **下载并安装落雪音乐**
   - 前往 [LX Music Releases](https://github.com/lyswhut/lx-music-desktop/releases) 下载最新版本

3. **启动程序**
   - 先启动落雪音乐（**必须先启动！**）
   - 双击 `启动点歌机.bat` 或运行 `python main.py`
   - 首次启动：
     - 扫描二维码登录B站（可选，登录后弹幕显示完整用户名）
     - 输入直播间房间号（自动保存，下次无需输入）

### 使用说明

#### 弹幕点歌
在直播间发送弹幕：
- `点歌 青花瓷` - 搜索并播放"青花瓷"
- `点歌 青花瓷 周杰伦` - 指定歌手，更精确

#### 弹幕切歌（房管专属）
拥有房管权限的用户发送：`下一首`

#### 歌曲黑名单
编辑 `.A歌曲黑名单.txt` 文件，一行一个歌名，在黑名单中的歌曲不会被点播。
**注意**：修改后需重启程序生效。

#### 命令行参数
```bash
# 直接指定房间号启动
python main.py 房间号
```

## 更新日志

### v2.03 (最新)
- ✨ 新增B站自动登录模块（扫码登录 + Cookie持久化 + 自动刷新）
- ✨ 新增酷狗音乐精确搜索（通过API获取完整歌曲信息）
- ✨ 房间号首次输入后自动保存到配置文件
- 🔒 移除硬编码的SESSDATA，使用更安全的登录方式
- ⚡ 异步点歌处理，不阻塞弹幕监听
- 🐛 修复黑名单判断后继续执行的bug
- 📝 新增一键启动脚本（bat文件）

### v2.0
- 调用 [blivedm](https://github.com/xfgryujk/blivedm) 获取实时弹幕（替代轮询方式）

### v1.02
- 新增弹幕切歌功能（房管权限）

### v1.01
- 新增歌曲黑名单功能
- 支持启动脚本中预设房间号

## 文件说明

```
blive-vod-fork/
├── main.py              # 主程序入口
├── bili_login.py        # B站登录模块（扫码/Cookie管理）
├── kg_search.py         # 酷狗音乐搜索模块
├── lxmusic.py           # LX Music Scheme URL封装
├── config.py            # 配置文件管理
├── version.py           # 版本检查
├── blivedm/             # B站直播弹幕客户端库
├── config.json          # 配置文件（自动生成）
├── cookies.json         # 登录凭证（自动生成，不上传git）
├── .A歌曲黑名单.txt     # 歌曲黑名单
├── 启动点歌机.bat       # 一键启动脚本
└── requirements.txt     # Python依赖列表
```

## 常见问题

### Q: 落雪音乐无法播放歌曲？
A: 参考 [LX Music Issues #5](https://github.com/lyswhut/lx-music-desktop/issues/5#issuecomment-2099784225)

### Q: 弹幕用户名显示为打码状态？
A: 首次启动时扫码登录B站账号即可显示完整用户名。登录信息会自动保存，后续启动无需重新登录。

### Q: Cookie过期怎么办？
A: 程序会自动检测并刷新Cookie。如果刷新失败，会提示重新扫码登录。

### Q: 如何更换监听的直播间？
A: 修改 `config.json` 中的 `roomid` 字段，或删除该字段后重启程序重新输入。

## 问题反馈

有任何问题可以提 [Issues](https://github.com/QDLinux/blive-vod-fork/issues)

## 致谢

- 原项目：[xuan06zyx/blive-vod](https://github.com/xuan06zyx/blive-vod)
- B站直播弹幕库：[xfgryujk/blivedm](https://github.com/xfgryujk/blivedm)
- 音乐播放器：[lyswhut/lx-music-desktop](https://github.com/lyswhut/lx-music-desktop)

<br>
⭐ **如果这个项目对你有帮助，欢迎点个 Star！** ⭐

## Stargazers over time
[![Stargazers over time](https://starchart.cc/xuan06zyx/blive-vod.svg?variant=adaptive)](https://starchart.cc/xuan06zyx/blive-vod)
