import os
import json
from app_dir import get_config_path


def create_config():
    file_path = get_config_path()

    if not os.path.exists(file_path):
        config_data = {
            "roomid": ""
        }
        with open(file_path, 'w', encoding='utf-8') as config_file:
            json.dump(config_data, config_file, indent=4, ensure_ascii=False)
        print(f"配置文件不存在，已新建{file_path}文件。")
