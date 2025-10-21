from utils.read_yaml import read_yaml
from utils.send_request import send_request


def test_captcha_get():
    case_data = read_yaml("captcha_get.yaml")
    send_request(case_data)