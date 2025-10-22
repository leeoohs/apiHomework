import copy
import os.path

import yaml

from config.setting import YAML_PATH


def load_ddt_cases(file_name: str) -> dict:
    """
    读取 YAML 用例文件，展开 ddts，不解析 context。
    返回列表，每个元素为：
      - template: 原始用例模板（含 context，保留 !var）
      - ddt_params: 当前 ddts 中的参数字典
      - desc: 用例描述
    """

    file_path = os.path.join(YAML_PATH, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # 移除 ddts 节点，得到基础模板
    base_template = {k: v for k, v in raw.items() if k != "ddts"}
    ddts = raw.get("ddts", [{}])

    case_data = []
    for ddt in ddts:
        new_case = copy.deepcopy(base_template)

        # 将 ddt 中的键值对覆盖同名字段
        for key, value in ddt.items():
            if key != "desc":
                new_case[key] = value

        # 保存描述信息
        new_case["_desc"] = ddt.get("desc", "No description")

        case_data.append(new_case)

    return case_data


if __name__ == '__main__':
    print(load_ddt_cases("captcha_get.yaml"))