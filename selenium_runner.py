import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

SMARTSTORE_URL = "https://sell.smartstore.naver.com/#/home/about"

_driver: Optional[webdriver.Chrome] = None  # 전역으로 1개만 유지


def _new_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--start-maximized")

    # 알림 팝업 방지(권장)
    prefs = {"profile.default_content_setting_values.notifications": 2}
    opts.add_experimental_option("prefs", prefs)

    # ✅ 프로필 공유를 안 하고도(=충돌 최소) “같은 세션”을 유지하려면
    # 드라이버를 1개만 띄워서 유지하는 게 핵심임
    return webdriver.Chrome(options=opts)


def get_driver() -> webdriver.Chrome:
    global _driver
    if _driver is None:
        _driver = _new_driver()
    return _driver


def open_smartstore() -> None:
    d = get_driver()
    d.get(SMARTSTORE_URL)


def check_logged_in() -> bool:
    d = get_driver()
    try:
        # ✅ 현재 화면은 건드리지 않고, 로그인 요소만 확인
        WebDriverWait(d, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//li[@ng-if='vm.loginInfo']//span[contains(@class,'login-id')]")
            )
        )
        return True
    except TimeoutException:
        return False
