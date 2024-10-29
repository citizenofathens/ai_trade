from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# 로그인 정보 설정
def add_firewall_exception():
    try:
        # 방화벽 예외 추가 명령어
#        cmd = 'netsh advfirewall firewall add rule name="ChromeDriver" dir=in action=allow program="[r"C:\Users\sminpark\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"]" enable=yes profile=any'
        cmd = r'netsh advfirewall firewall add rule name="ChromeDriver" dir=in action=allow program="C:\Users\sminpark\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe" enable=yes profile=any'

        subprocess.run(cmd, shell=True, check=True)
        print("방화벽 예외가 추가되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"방화벽 예외 추가 실패: {e}")


# def site_login(username,password,driver):
#
#     return driver


# ChromeDriver 실행 전에 방화벽 예외 추가
add_firewall_exception()

# ChromeDriver 설정 및 실행
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-popup-blocking")  # 팝업 차단 비활성화해서 구글 로그인 창뜨도록
#Google이 Selenium을 감지하지 못하도록 Chrome의 사용자 에이전트를 일반 브라우저처럼 위장할 수 있습니다.
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")  # 일반 브라우저 User-Agent로 변경
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
chrome_options.add_argument("user-data-dir=C:/Users/YourUsername/AppData/Local/Google/Chrome/User Data")  # 자신의 Chrome 프로필 경로를 지정


driver = webdriver.Chrome(options=chrome_options)
# ChromeDriver 실행
    # TradingView 홈페이지로 이동

    # 구글로그인을 먼저하기?
    # 이 auth 토큰 만료되면 url 사용못함
    #oauth_url =" https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=929030140737-lmcn34f4krhe9a5rokco9fu95k1uq7l9.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A60530%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&state=y90kTvEuv7VBaOQux8YGivzHSVjzxN&access_type=offline"
  #  driver.get(oauth_url)

wait = WebDriverWait(driver, 10)  # 최대 10초 대기


driver.get("https://kr.tradingview.com")
# WebDriverWait 사용하여 로그인 버튼이 나타날 때까지 대기
wait = WebDriverWait(driver, 3)  # 최대 10초 대기
# 로그인 버튼 찾기 및 클릭
print("로그인 버튼 찾는 중...")
login_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[3]/div[2]/div[3]/button[2]")))
login_button.click()
print("로그인 버튼 클릭 완료")
# 페이지 로드 대기 및 스크롤로 이메일 옵션 표시
time.sleep(2)
print("이메일 옵션 찾는 중...")
xpath_selector='/html/body/div[7]/div[3]/span/div[1]/div/div/div/div/button[1]/span/span/span/span[2]/span[1]/span'

email_option = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_selector)))

driver.execute_script("arguments[0].scrollIntoView(true);", email_option)
email_option.click()
print("이메일 옵션 클릭 완료")

email_option.click()
print("이메일 옵션 클릭 완료")# 약간의 대기 후 iframe 전환 시도
time.sleep(2)

# 새로운 페이지로 이동한 후 충분히 대기
time.sleep(2)



# 모든 iframe 순회 및 요소 찾기
print("iframe을 순회하며 요소 찾는 중...")
found = False
for index, frame in enumerate(driver.find_elements(By.TAG_NAME, "iframe")):
    driver.switch_to.default_content()  # 메인 컨텐츠로 돌아가기
    driver.switch_to.frame(frame)  # 각 iframe으로 전환
    print(f"{index + 1}번째 iframe으로 전환 시도")
    # iframe 전환후 구글창이열렸다
    try:
        # 원하는 요소가 있는지 확인
        target_element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div[2]/span[1]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
        driver.execute_script("arguments[0].click();", target_element)
        print("요소 클릭 완료")
        found = True
        break  #
    except Exception as e:
        print(f"{index + 1}번째 iframe에 요소가 없습니다. 다음 iframe을 확인합니다.")
        continue  # 다음 iframe으로 이동

    if not found:
        print("모든 iframe을 확인했지만 요소를 찾지 못했습니다.")

# 새 창이 열리길 기다림
time.sleep(5)  # 창 열림 대기

# 현재 열려 있는 창 핸들 가져오기
current_windows = driver.window_handles

# 새로운 창이 열렸는지 확인
if len(current_windows) > 1:
    driver.switch_to.window(current_windows[-1])
    print("새 창으로 전환 완료 (Google Auth 창)")
else:
    print("새 창이 열리지 않았습니다. 팝업 차단 여부를 확인해 주세요.")


# 또는 ActionChains로 클릭 시도
email_login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]')))
actions = ActionChains(driver)
actions.move_to_element(email_login_button).click().perform()  # 강화된 클릭
print("ActionChains로 클릭 시도 완료")

time.sleep(3000)

print("이메일 로그인 버튼 클릭 완료")

#driver_1 = open_browser(chromedriver_path)
#    driver_2 = site_login(username, password, driver)
#get_csv(driver_2)


# 요소가 클릭 가능한 상태인지 확인



# 이메일 입력
email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
email_input.send_keys(email)

# 비밀번호 입력
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys(password)
password_input.send_keys(Keys.RETURN)
time.sleep(5)

# 차트 URL로 이동
chart_url = "https://kr.tradingview.com/chart/YsoP4fau/?symbol=BINANCE%3ABTCUSDT.P"
driver.get(chart_url)
time.sleep(5)

# 전체 페이지 캡처
screenshot_path = "tradingview_chart_fullpage.png"
driver.save_screenshot(screenshot_path)
print(f"전체 화면 캡처가 저장되었습니다: {screenshot_path}")



#finally:
    # 브라우저 닫기
driver.quit()