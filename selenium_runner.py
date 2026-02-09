# selenium_runner.py
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

SMARTSTORE_URL = "https://sell.smartstore.naver.com/#/home/about"
_driver: Optional[webdriver.Chrome] = None


def _new_driver() -> webdriver.Chrome:
    opts = Options()

    # ✅ 시크릿 모드
    opts.add_argument("--incognito")

    # 창 최대화
    opts.add_argument("--start-maximized")

    # 알림 차단
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    opts.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=opts)


def get_driver() -> webdriver.Chrome:
    global _driver
    if _driver is None:
        _driver = _new_driver()
    return _driver


def open_smartstore() -> None:
    d = get_driver()
    d.get(SMARTSTORE_URL)


def _safe_click(d: webdriver.Chrome, el) -> None:
    try:
        el.click()
    except ElementClickInterceptedException:
        d.execute_script("arguments[0].click();", el)


def _wait_ready_for_category_search(wait: WebDriverWait) -> None:
    # 카테고리 섹션/라벨이 뜰 때까지 대기 (DOM 기준)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "label[for='r_1_1']")
        )
    )


def ensure_category_panel_open() -> None:
    d = get_driver()
    wait = WebDriverWait(d, 25)

    _wait_ready_for_category_search(wait)

    def _toggle_el():
        return wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-default.btn-hide"))
        )

    toggle = _toggle_el()
    if "active" in (toggle.get_attribute("class") or ""):
        return

    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-default.btn-hide")))
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", toggle)
        _safe_click(d, toggle)
    except Exception:
        ActionChains(d).move_to_element(toggle).click().perform()

    # 클릭 후 DOM이 바뀔 수 있으니 재획득해서 확인
    wait.until(lambda _d: "active" in (_toggle_el().get_attribute("class") or ""))

def go_product_register() -> None:
    """
    좌측 메뉴: 상품관리 → 상품 등록(#/products/create) 이동 후
    카테고리 섹션이 조작 가능한 상태까지 대기
    """
    d = get_driver()
    wait = WebDriverWait(d, 25)

    # 좌측 메뉴 로딩
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='상품관리']")))

    # 상품관리 클릭
    product_manage = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='seller-lnb']//a[normalize-space()='상품관리']"))
    )
    _safe_click(d, product_manage)

    # 상품 등록 클릭
    product_register = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@id='seller-lnb']//a[@href='#/products/create' and normalize-space()='상품 등록']")
        )
    )
    _safe_click(d, product_register)

    # 상품등록 화면 + 카테고리 검색 탭 준비 대기
    _wait_ready_for_category_search(wait)

    # 카테고리 패널이 닫혀있으면 열어둠(안정)
    ensure_category_panel_open()


def check_logged_in() -> bool:
    d = get_driver()
    try:
        WebDriverWait(d, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.login-id"))
        )
        return True
    except TimeoutException:
        return False


def set_category_by_query(query: str) -> None:
    d = get_driver()
    wait = WebDriverWait(d, 25)

    q = (query or "").strip()
    if not q:
        raise ValueError("query is empty")

    _wait_ready_for_category_search(wait)
    ensure_category_panel_open()

    # 검색 탭 클릭
    label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='r_1_1']")))
    _safe_click(d, label)

    # selectize 박스 클릭(포커스)
    box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.selectize-input")))
    box.click()

    # ✅ 기존 선택 완전 제거 (item이 남아 있으면 재선택 실패)
    for _ in range(5):
        try:
            rm = d.find_element(By.CSS_SELECTOR, "div.selectize-input a.remove")
            _safe_click(d, rm)
            continue
        except Exception:
            pass

        # remove 버튼이 없으면 backspace로 제거 시도
        try:
            if d.find_elements(By.CSS_SELECTOR, "div.selectize-input div.item"):
                d.switch_to.active_element.send_keys(Keys.BACKSPACE)
                continue
        except Exception:
            pass

        # item이 없으면 종료
        if not d.find_elements(By.CSS_SELECTOR, "div.selectize-input div.item"):
            break

    # 입력
    inp = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.selectize-input input[placeholder='카테고리명 입력']")
        )
    )
    inp.click()
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.BACKSPACE)
    inp.send_keys(q)

    # 옵션 클릭
    option = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@class,'selectize-dropdown') and contains(@style,'display: block')]"
            "//div[contains(@class,'selectize-dropdown-content')]"
            f"//div[contains(@class,'option') and @data-selectable and contains(normalize-space(), {repr(q)})]"
        ))
    )
    _safe_click(d, option)

    # item 생성 확인
    wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//div[contains(@class,'selectize-input')]//div[contains(@class,'item') and contains(normalize-space(), {repr(q)})]"
        ))
    )

    # 입력
    inp = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.selectize-input input[placeholder='카테고리명 입력']")))
    inp.click()
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.BACKSPACE)
    inp.send_keys(q)

    # 옵션 클릭(contains로 안정)
    option = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@class,'selectize-dropdown') and contains(@style,'display: block')]"
            "//div[contains(@class,'selectize-dropdown-content')]"
            f"//div[contains(@class,'option') and @data-selectable and contains(normalize-space(), {repr(q)})]"
        ))
    )
    _safe_click(d, option)

    # item 생성 확인
    wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//div[contains(@class,'selectize-input')]//div[contains(@class,'item') and contains(normalize-space(), {repr(q)})]"
        ))
    )
def go_register_and_set_category(query: str) -> None:
    """
    원샷:
    1) 상품등록 페이지로 이동
    2) 카테고리 패널 열기/검색 탭 준비
    3) query로 카테고리 검색 후 추천값 선택
    """
    go_product_register()
    set_category_by_query(query)
