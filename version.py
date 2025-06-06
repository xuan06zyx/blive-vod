import questionary
import requests
import json


def version(currentVersion: float, release_api: str):
    gh = 'https://github.com/xuan06zyx/blive-vod/releases'
    gt = 'https://gitee.com/zyXuan06/blive-vod/releases'
    # 版本管理
    github_url = 'https://api.github.com/repos/xuan06zyx/blive-vod/releases/latest'
    gitee_url = 'https://gitee.com/api/v5/repos/zyXuan06/blive-vod/releases/latest'
    # 判断版本管理渠道
    if release_api == 'Github(Global)':
        release_url = github_url
        releases_url = gh
    elif release_api == 'Gitee(China)':
        release_url = gitee_url
        releases_url = gt
    else:
        release_api = questionary.select("选择版本管理渠道", ['Github(Global)', 'Gitee(China)']).ask()
        if release_api == 'Github(Global)':
            release_url = github_url
            releases_url = gh
        elif release_api == 'Gitee(China)':
            release_url = gitee_url
            releases_url = gt
        with open('config.json', 'r', encoding='utf-8') as r:
            config = json.load(r)
        config["release_api"] = release_api
        with open('config.json', 'w', encoding='utf-8') as w:
            json.dump(config, w, indent=4)

    res = requests.get(release_url)
    latest_version = res.json()['name']
    if float(currentVersion) < float(latest_version):
        print(
            f'有可用更新,当前版本为{currentVersion},最新版本为{latest_version}\n请前往 {releases_url} 下载最新版')
    else:
        print(f'当前版本为:{currentVersion},最新版本为{latest_version},渠道:{release_api}')


if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as r:
        config = json.load(r)
    version(config['version'], config['release_api'])
