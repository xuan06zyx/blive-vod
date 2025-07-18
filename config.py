import os
import json


def create_config(version: float):
    # 获取当前脚本的目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 指定config.json文件的路径
    file_path = os.path.join(current_dir, "config.json")

    # 检查文件是否存在
    if not os.path.exists('./config.json'):
        # 如果文件不存在，则创建一个新的config.json文件
        config_data = {
            "version": version,
            "release_api": "",
            "roomid": ""
        }
        with open(file_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        print(f"配置文件不存在，已新建{file_path}文件。")
