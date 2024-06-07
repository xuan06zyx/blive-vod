import get_barrage
import webbrowser
import requests
import lxmusic
import sys
import re


version = 1.02
# 版本检查
res = requests.get('https://api.github.com/repos/xuan06zyx/blive-vod/releases')
latest_version = res.json()[0]['name']
if float(version) < float(latest_version):
    print(f'有可用更新,当前版本为{version},最新版本为{latest_version}\n请前往 https://github.com/xuan06zyx/blive-vod/releases 下载最新版')
else:
    print(f'当前版本为最新版本{version}')

if len(sys.argv) > 1:
    roomid = sys.argv[1]
else:
    roomid = input("请输入B站直播间号(回车确认):")
get_barrage = get_barrage.Get_Barrage(roomid)
lxmusic = lxmusic.lxmusic()

timeline = ''
barrage_list = []
barrage_text_list = []
last_song = ''
song_list = []
BlackSong_list = []
# 打开黑名单文件并读取内容
with open('.A歌曲黑名单.txt', 'r', encoding='utf-8') as Blacklist:
    Blacklist_lines = Blacklist.readlines()
for line in Blacklist_lines:
    BlackSong = line.strip()  # 去除行末的换行符和多余的空格
    BlackSong_list.append(BlackSong)

for _ in get_barrage:
    # 弹幕列表变化以后触发迭代并调用方法
    barrage_ = next(get_barrage)
    admin = barrage_["admin"]
    barrage_name = barrage_["barrage_name"]
    barrage_list = barrage_["barrage_list"]
    barrage_text_list = barrage_["barrage_text_list"]
    if barrage_text_list:
        # 弹幕切歌
        if admin[-1]["text"] == '下一首' and admin[-1]["timeline"] != timeline:
            print(f'收到切歌请求, 发送者:{admin[-1]["nickname"]}')
            timeline = admin[-1]["timeline"]
            webbrowser.open(url='lxmusic://player/skipNext')

        # 弹幕点歌
        # 正则表达式
        diange = re.search(r'^点歌\s+(.*)', barrage_text_list[-1])
        if diange and last_song != diange.group(1) and diange.group(1):
            song_name = diange.group(1)  # 匹配点歌关键词
            last_song = song_name
            # 判断屏蔽词
            if song_name in BlackSong_list:
                print(f'发现屏蔽词:{song_name},发送者:{barrage_name}')
                continue
            print('收到点歌请求:', song_name)
            Scheme_url = lxmusic.music_searchPlay(name=song_name, playLater=True)  # 调用封装好的落雪音乐模块
            webbrowser.open(url=Scheme_url)  # 使用webbrowser打开Scheme URL

            song_list.append(song_name)  # 写入歌单列表
