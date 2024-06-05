import get_barrage
import webbrowser
import lxmusic
import time
import sys
import re


if len(sys.argv) > 1:
    roomid = sys.argv[1]
else:
    roomid = input("请输入B站直播间号(回车确认):")
get_barrage = get_barrage.Get_Barrage(roomid)
lxmusic = lxmusic.lxmusic()

barrage_list = []
barrage_text_list = []
last_song = ''
song_list = []
BlackSong_list = []
# 打开黑名单文件并读取内容
with open('.A歌曲黑名单.txt', 'r', encoding='utf-8') as Blacklist:
    Blacklist_lines = Blacklist.readlines()
for line in Blacklist_lines:
    # 去除行末的换行符和多余的空格
    BlackSong = line.strip()
    BlackSong_list.append(BlackSong)

for _ in get_barrage:
    # 弹幕列表变化以后触发迭代并调用方法
    barrage_ = next(get_barrage)
    barrage_list = barrage_["barrage_list"]
    barrage_text_list = barrage_["barrage_text_list"]
    if barrage_text_list:
        diange = re.search(r'^点歌\s+(.*)', barrage_text_list[-1])
        if diange and last_song != diange.group(1) and diange.group(1) not in BlackSong_list:
            # 正则表达式
            song_name = diange.group(1)  # 匹配点歌关键词
            last_song = song_name

            print('收到点歌请求:', song_name)
            Scheme_url = lxmusic.music_searchPlay(name=song_name, playLater=True)  # 调用封装好的落雪音乐模块
            webbrowser.open(url=Scheme_url)  # 使用webbrowser打开Scheme URL
            # 写入歌单列表
            song_list.append(song_name)
