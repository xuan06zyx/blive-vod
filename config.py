import os
import json
from app_dir import get_config_path, get_blacklist_path


def create_config():
    file_path = get_config_path()

    if not os.path.exists(file_path):
        config_data = {
            "roomid": ""
        }
        with open(file_path, 'w', encoding='utf-8') as config_file:
            json.dump(config_data, config_file, indent=4, ensure_ascii=False)
        print(f"配置文件不存在，已新建{file_path}文件。")

    # 自动创建歌曲黑名单文件
    blacklist_path = get_blacklist_path()
    if not os.path.exists(blacklist_path):
        with open(blacklist_path, 'w', encoding='utf-8') as f:
            f.write("")
        print(f"黑名单文件不存在，已新建{blacklist_path}文件。")
