import os.path

import yaml

from config.setting import YAML_PATH


def read_yaml(file_name: str) -> dict:
    """
    读取YAML文件并返回字典格式的内容
    
    参数:
        file_name (str): YAML文件名
        
    返回:
        dict: YAML文件内容的字典表示
    """
    file_path = os.path.join(YAML_PATH, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        case_data = yaml.safe_load(f)
    return case_data