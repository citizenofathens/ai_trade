from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import time

# Google API OAuth 설정
CLIENT_SECRET_FILE = r"C:\Users\sminpark\Downloads\client_secret_929030140737-lmcn34f4krhe9a5rokco9fu95k1uq7l9.apps.googleusercontent.com.json"   # 실제 client_secret.json 파일 경로로 변경
SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument("--disable-popup-blocking")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)  # 최대 대기 시간 설정



def google_authenticate():
    creds = None

    # 토큰 파일이 있으면 로드하여 인증 시도
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # 인증이 없거나 유효하지 않을 경우 재인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰을 저장하여 이후 재사용 가능
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    print("Google 인증 성공")
    return creds

# Google 인증 수행
creds = google_authenticate()

# TradingView 사이트로 이동 후 로그인 과정 진행
try:
    driver.get("https://kr.tradingview.com")
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[3]/div[2]/div[3]/button[2]"))).click()
    print("로그인 버튼 클릭 완료")

    # 이메일 로그인 버튼 찾기
    time.sleep(2)
    email_option = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                          '/html/body/div[7]/div[3]/span/div[1]/div/div/div/div/button[1]/span/span/span/span[2]/span[1]/span')))
    driver.execute_script("arguments[0].scrollIntoView(true);", email_option)
    email_option.click()
    print("이메일 옵션 클릭 완료")

    # 구글 인증 창 대기
    time.sleep(2)

    # 새로운 페이지의 모든 iframe 순회 및 구글 버튼 클릭
    found = False
    for index, frame in enumerate(driver.find_elements(By.TAG_NAME, "iframe")):
        driver.switch_to.default_content()
        driver.switch_to.frame(frame)
        print(f"{index + 1}번째 iframe으로 전환 시도")

        try:
            target_element = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/span[1]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
            driver.execute_script("arguments[0].click();", target_element)
            print("구글 로그인 버튼 클릭 완료")
            found = True
            break
        except TimeoutException:
            print(f"{index + 1}번째 iframe에 요소가 없습니다. 다음 iframe을 확인합니다.")
            continue

    if not found:
        print("모든 iframe을 확인했지만 요소를 찾지 못했습니다.")

except Exception as e:
    print("오류 발생:", e)

finally:
    driver.quit()
