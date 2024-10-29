from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import time
def add_firewall_exception():
    try:
        # 방화벽 예외 추가 명령어

#        cmd = 'netsh advfirewall firewall add rule name="ChromeDriver" dir=in action=allow program="[r"C:\Users\sminpark\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"]" enable=yes profile=any'
        cmd = r'netsh advfirewall firewall add rule name="ChromeDriver" dir=in action=allow program="C:\Users\sminpark\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe" enable=yes profile=any'

        subprocess.run(cmd, shell=True, check=True)
        print("방화벽 예외가 추가되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"방화벽 예외 추가 실패: {e}")

# ChromeDriver 실행 전에 방화벽 예외 추가
add_firewall_exception()

# ChromeDriver 설정 및 실행
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(options=chrome_options)


try:
    # TradingView URL로 이동
    url = "https://kr.tradingview.com/chart/YsoP4fau/?symbol=BINANCE%3ABTCUSDT.P"
    browser.get(url)

    # 페이지가 완전히 로드될 때까지 잠시 대기
    time.sleep(5)

    # 전체 페이지 캡처
    screenshot_path = "tradingview_chart_fullpage.png"
    browser.save_screenshot(screenshot_path)
    print(f"전체 화면 캡처가 저장되었습니다: {screenshot_path}")

finally:
    # 브라우저 닫기
    browser.quit()