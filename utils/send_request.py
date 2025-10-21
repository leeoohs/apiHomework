import requests
from jsonpath import jsonpath

from config.setting import BASE_URL


def send_request(case_data):
    """
    发送请求
    :param method: 请求方法
    :param url: 请求地址
    :param data: 请求数据
    :param json: 请求json数据
    :param kwargs: 其他参数
    :return: 响应对象
    """
    # 拼接完整请求地址
    url = BASE_URL + case_data['url'] if case_data['url'].startswith('/') else case_data['url']

    # 请求方法
    method = case_data.get("method", "").upper()
    if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        raise ValueError(f"不支持的请求方法：{method}，支持的方法：GET/POST/PUT/DELETE/PATCH")

    # 提取请求参数
    method = case_data['method'].upper()  # 转大写（避免YAML中写小写）
    headers = case_data.get('headers', {})
    body = case_data.get('body', {})
    json_data = body.get('json', None)
    form_data = body.get('form', None)
    params = body.get('params', None)
    cookies = case_data.get('cookies', None)
    timeout = case_data.get('timeout', 10)

    # 发送请求
    request_kwargs = {
        "method": method,
        "url": url,
        "headers": headers,
        "params": params,
        "data": body,
        "json": json_data,
        "timeout": timeout,
        "cookies": cookies,
    }
    # 处理请求体（POST/PUT等方法）
    if method in ["POST", "PUT", "PATCH"]:
        if json_data is not None:
            request_kwargs["json"] = json_data
        if form_data is not None:
            request_kwargs["data"] = form_data

    response = requests.request(**request_kwargs)
    print("接口响应：", response.text)

    # 断言
    assertions = case_data.get("assert", [])
    if not assertions:
        return response

    # 解析响应体为JSON
    try:
        response_json = response.json()
    except ValueError:
        response_json = None

    for idx, assert_item in enumerate(assertions, 1):
        # 校验断言配置完整性
        required_keys = ["target", "expected", "type"]
        missing_keys = [k for k in required_keys if k not in assert_item]
        if missing_keys:
            raise ValueError(f"第{idx}条断言缺失必要字段：{missing_keys}")

        target = assert_item["target"]
        expected = assert_item["expected"]
        assert_type = assert_item["type"].lower()

        # 提取实际值
        # 替换原提取实际值的代码段
        try:
            if target == "status_code":
                actual = response.status_code
            elif target.startswith(("$", ".")):  # JSONPath表达式
                if response_json is None:
                    raise ValueError("响应体非JSON格式，无法使用JSONPath")
                matches = jsonpath(response_json, target)
                if matches is None:
                    raise ValueError(f"JSONPath '{target}' 未匹配到结果")

                # 关键修复：兼容非列表类型的结果（如bool、None等）
                if isinstance(matches, list):
                    actual = matches[0] if len(matches) == 1 else matches
                else:
                    actual = matches  # 直接使用非列表结果（如bool、数字、字符串等）
            else:
                raise ValueError(f"不支持的target类型: {target}（支持status_code和JSONPath）")
        except Exception as e:
            raise AssertionError(f"第{idx}条断言提取值失败：{str(e)}")

        # 执行断言逻辑
        try:
            if assert_type == "equal":
                assert actual == expected, f"实际值{actual}≠预期值{expected}"
            elif assert_type == "not_equal":
                assert actual != expected, f"实际值{actual}不应等于预期值{expected}"
            elif assert_type == "contains":
                if isinstance(actual, list):
                    assert expected in actual, f"列表{actual}不包含{expected}"
                else:
                    assert str(expected) in str(actual), f"{actual}不包含{expected}"
            elif assert_type == "is_not_none":
                assert actual is not None, f"实际值应为非None，却为{actual}"
            elif assert_type == "greater_than":
                assert isinstance(actual, (int, float)) and isinstance(expected, (int, float)), \
                    "greater_than仅支持数字类型"
                assert actual > expected, f"{actual}不应≤{expected}"
            # 在原有的assert_type判断中增加以下分支
            elif assert_type == "type_equal":
                # 校验字段类型（expected为"str"/"int"/"bool"等）
                type_map = {
                    "str": str,
                    "int": int,
                    "bool": bool,
                    "dict": dict,
                    "list": list
                }
                if expected not in type_map:
                    raise ValueError(f"不支持的类型校验：{expected}，支持类型：{list(type_map.keys())}")
                assert isinstance(actual, type_map[expected]), \
                    f"字段类型不匹配，预期{expected}，实际{type(actual).__name__}"

            elif assert_type == "starts_with":
                # 校验字符串前缀
                assert isinstance(actual, str), "starts_with仅支持字符串类型"
                assert actual.startswith(expected), \
                    f"字符串{actual}不以{expected}开头"
            else:
                raise ValueError(f"不支持的断言类型: {assert_type}")
        except AssertionError as e:
            raise AssertionError(f"第{idx}条断言失败：{str(e)}")

    return response
