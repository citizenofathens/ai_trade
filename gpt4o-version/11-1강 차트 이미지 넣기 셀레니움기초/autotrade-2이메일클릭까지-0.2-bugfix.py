from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import time
import os
import subprocess
from webdriver_manager.chrome import ChromeDriverManager


def setup_chrome_driver():
    chrome_options = Options()

    # Chrome 충돌 방지 옵션
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')

    # 크래시 방지
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    # DevTools 포트 설정
    chrome_options.add_argument('--remote-debugging-port=9222')

    # 프로세스 종료 방지
    chrome_options.add_experimental_option("detach", True)

    # Chrome binary 위치 직접 지정
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    try:
        # ChromeDriver 자동 설치 및 서비스 생성
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome 드라이버 설정 실패: {e}")
        raise


def login_to_tradingview(driver, wait_time=10):
    wait = WebDriverWait(driver, wait_time)

    try:
        # TradingView 접속
        driver.get("https://kr.tradingview.com")
        time.sleep(3)

        # 로그인 버튼 클릭
        print("로그인 버튼 찾는 중...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[3]/div[2]/div[3]/button[2]"))
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", login_button)
        print("로그인 버튼 클릭 완료")

        # 이메일 옵션 선택
        print("이메일 옵션 찾는 중...")
        email_option = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/div[7]/div[3]/span/div[1]/div/div/div/div/button[1]/span/span/span/span[2]/span[1]/span'))
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", email_option)
        print("이메일 옵션 클릭 완료")

        time.sleep(2)

        # iframe 찾기 및 Google 로그인 버튼 클릭
        print("iframe을 순회하며 요소 찾는 중...")
        found = False
        for index, frame in enumerate(driver.find_elements(By.TAG_NAME, "iframe")):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                print(f"{index + 1}번째 iframe으로 전환 시도")

                target_element = wait.until(
                    EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div[2]/span[1]'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                driver.execute_script("arguments[0].click();", target_element)
                print("요소 클릭 완료")
                found = True
                break
            except Exception as e:
                print(f"{index + 1}번째 iframe에서 요소를 찾지 못했습니다: {e}")
                continue

        if not found:
            print("모든 iframe을 확인했지만 요소를 찾지 못했습니다.")
            return False

        # 새 창이 열리길 기다림
        time.sleep(3)
        windows = driver.window_handles

        if len(windows) > 1:
            driver.switch_to.window(windows[-1])
            print("새 창으로 전환 완료")

            # 이메일 입력
            print("이메일 입력 중...")
            email_input = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div[1]/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input'))
            )
            email_input.send_keys("tjdals0219@gmail.com")
            next_button = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button/span"))
            )
            next_button.click()

            print("이메일 입력 완료")

        else:
            print("새 창이 열리지 않았습니다")
            return False

        return True

    except Exception as e:
        print(f"로그인 중 오류 발생: {e}")
        return False


def main():
    try:
        # 기존 Chrome 프로세스 종료
        try:
            subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], capture_output=True)
            time.sleep(2)
        except:
            pass

        # ChromeDriver 설정
        print("Chrome 드라이버 설정 중...")
        driver = setup_chrome_driver()

        success = login_to_tradingview(driver)

        if success:
            print("로그인 진행 중...")
        else:
            print("로그인 실패")

    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass


if __name__ == "__main__":
    # webdriver-manager 설치 확인
    try:
        import webdriver_manager
    except ImportError:
        print("webdriver-manager 설치 중...")
        subprocess.check_call(['pip', 'install', 'webdriver-manager'])

    main()