from urllib.parse import quote
import json


# 接口文档 https://lxmusic.toside.cn/desktop/scheme-url
class lxmusic:
    def Scheme_url(self, url,  data):
        """
        生成Scheme url
        :param url: 调用的url
        :param data: 其它方法传来的数据
        :return: 编码后的Scheme url
        """
        url = f'lxmusic://{url}?data=' + quote(f'{json.dumps(data, ensure_ascii=False)}')
        print("编码后的url:", url)
        return url

    def songlist_open(self, source="", id="", url=""):
        """
        打开歌单
        :param source: 源，支持kw/kg/tx/wy/mg
        :param id: 歌单id
        :param url: 歌单链接 url和id必须传一个
        :return:songlist/open
        """
        data = {
            "source": source,  # 支持 kw/kg/tx/wy/mg
            "id": id,
            "url": url,  # id和url必须传一个
        }

        return self.Scheme_url('songlist/open', data)

    def songlist_play(self, source="", id="", url="", index=0):
        """
        播放歌单
        :param source: 源，支持kw/kg/tx/wy/mg
        :param id: 歌单id
        :param url: 歌单链接 url和id必须传一个
        :param index: # 播放第几首，从0开始
        :return:songlist/play
        """
        data = {
            "source": source,  # 支持 kw/kg/tx/wy/mg
            "id": id,
            "url": url,  # id和url必须传一个
            "index": index,  # 播放第几首，从0开始
        }

        return self.Scheme_url('songlist/play', data)

    def music_search(self, source="", name=""):
        """
        搜索音乐
        :param source: 源，支持kw/kg/tx/wy/mg
        :param name: 歌名
        :return:
        """
        data = {
            "source": source,
            "keywords": name,
        }

        return self.Scheme_url('music/search', data)

    def music_play(self, source="", name="", singer="", songmid="", img="", albumId="", interval="", albumName="",
                  types=None, hash="", strMediaMid="", copyrightId="", lrcUrl=""):
        """
        播放音乐
        :param source: 源，支持kw/kg/tx/wy/mg
        :param name: 歌曲名，必须
        :param singer: 艺术家，必须
        :param songmid: 歌曲id，必须
        :param img: 歌曲图片链接，选传
        :param albumId: 歌曲专辑id，选传
        :param interval: 格式化后歌曲时长，选传，例如 03:55
        :param albumName: 歌曲专辑名称，选传
        :param types: type 128k/320k/flac/flac24bit
        :param hash: kg必须
        :param strMediaMid: tx必传
        :param copyrightId: x选传
        :param lrcUrl: mg选传
        :return:music/play
        """
        if types is None:
            types = [{"type": "flac24bit", "size": "", "hash": ""}]
        data = {
                "source": source,  # 源，必须
                "name": name,  # 歌曲名，必须
                "singer": singer,  # 艺术家，必须
                "songmid": songmid,  # 歌曲id，必须
                "img": img,  # 歌曲图片了解，选传
                "albumId": albumId,  # 歌曲专辑id，选传
                "interval": interval,  # 格式化后歌曲时长，选传，例如 03:55
                "albumName": albumName,  # 歌曲专辑名称，选传
                "types": types,  # type 128k/320k/flac/flac24bit
                "hash": hash,  # kg必须
                "strMediaMid": strMediaMid,  # tx必传
                "copyrightId": copyrightId,  # tx选传
                "lrcUrl": lrcUrl,  # mg选传
            }
        return self.Scheme_url('music/play', data)

    def music_searchPlay(self, name="", singer="", albumName="", interval="", playLater=False):
        """
        搜索音乐并播放
        :param name:（歌曲名，必须）
        :param singer:（歌手，可选）
        :param albumName:（专辑名，可选）
        :param interval:（时长，xx:xx 的形式，可选）
        :param playLater:（是否稍后播放，可选，默认 false 立即播放）
        :return:music/searchPlay
        """
        data = {
            "name": name,
            "singer": singer,
            "albumName": albumName,
            "interval": interval,
            "playLater": playLater
        }
        return self.Scheme_url('music/searchPlay', data)
