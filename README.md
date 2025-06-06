<div align="center">

<h1>Blive-Vod</h1>
<h1>阿B直播弹幕点歌机</h1>

</div>

*****本程序由纯Python制作而成，项目还在开发测试中极度不成熟，推荐有一定代码基础的用户使用本软件*****
## 免责声明

本软件仅供学习交流使用，请于下载后24小时内删除，不得用于任何商业用途，否则后果自负。

## 功能

- [x] 监控弹幕
- [x] 弹幕点歌
- [x] 弹幕切歌
- [x] 歌曲黑名单
- [ ] 前端展示歌单
- [ ] 制作UI

## 使用说明
1. 本项目歌曲播放功能通过调用[落雪音乐桌面版](https://github.com/lyswhut/lx-music-desktop)2.8.0+完成
2. 本项目仅能在win10/11 x64平台上运行，其它平台自行研究
3. 使用配置完成的程序(包含[python](https://www.python.org/downloads/windows/)环境和[lxmusic](https://github.com/lyswhut/lx-music-desktop/releases))
   1. 下载[发布页面](https://github.com/xuan06zyx/blive-vod/releases)中名称带env的压缩文件解压
   2. 启动lx-music-desktop.exe(一定要先启动落雪音乐再启动本程序!!!)
   3. 启动点歌机后输入房间号回车 等待程序输出roomid之类的信息即可
   4. 后续更新下载不带env的压缩文件替换
4. 1.01新增.A歌曲黑名单.txt 内的歌名不会触发点歌 用回车分隔歌名 一行一个(即屏蔽词 修改屏蔽词文件需重启程序生效)
5. 1.01新增在启动脚本的中填写直播间号 这样后续将不再需要手动输入 例如:
   ```cmd
   powershell ./python/python.exe main.py 123456
   
   pause
   ```
6. 2.0开始调用[blivedm](https://github.com/xfgryujk/blivedm)获取实时弹幕
7. 推荐有代码基础的用户可以clone本仓库,自行下载[落雪音乐](https://github.com/lyswhut/lx-music-desktop)
8. 在目标直播间发送弹幕点歌 歌名 歌手即可，如`点歌 青花瓷 周杰伦` 歌手可以不写 程序会自动搜索
9. 1.02版本新增弹幕切歌功能 拥有房管权限的用户发送弹幕`下一首`来切歌

## 问题反馈

1. 有任何问题都可以提[issues](https://github.com/xuan06zyx/blive-vod/issues)（新手程序员很少会看）
2. 国内用户可以加我[QQ](https://api.lolimi.cn/API/tzmp/api.php?qq=2015441509)
3. 落雪音乐无法播放歌曲？[点此](https://github.com/lyswhut/lx-music-desktop/issues/5#issuecomment-2099784225)

## 注意事项
1. 2.0版本后，接口是实时弹幕
~~1. 由于接口是弹幕历史记录，如果历史记录中最新一条弹幕含有点歌/下一首等触发词会直接触发功能~~
~~2. 有懂websocket以及会调用实时弹幕接口的大神联系我qwq~~
<br>
⭐**如果喜欢，点个star~**⭐

## Stargazers over time
[![Stargazers over time](https://starchart.cc/xuan06zyx/blive-vod.svg?variant=adaptive)](https://starchart.cc/xuan06zyx/blive-vod)
