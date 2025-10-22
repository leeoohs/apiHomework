import pytest

from utils.read_yaml import load_ddt_cases
from utils.send_request import send_request

test_cases = load_ddt_cases("captcha_get.yaml")


@pytest.mark.parametrize("case_data", test_cases)
def test_captcha_get(case_data):
    print("当前用例:", case_data.get("_desc"))
    send_request(case_data)