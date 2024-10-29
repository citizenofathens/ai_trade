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
from youtube_transcript_api import YouTubeTranscriptApi

from openai import OpenAI

# 로그인 정보 설정
# xpath로 이동할수있는요소를 정확히클릭해야함
import os
from datetime import datetime

import base64

def cleanup_chrome():
    """Chrome 관련 프로세스와 임시 파일 정리"""
    try:
        # Chrome 프로세스 종료
        subprocess.run('taskkill /f /im chrome.exe', shell=True, stderr=subprocess.DEVNULL)
        subprocess.run('taskkill /f /im chromedriver.exe', shell=True, stderr=subprocess.DEVNULL)

        # Chrome 임시 파일 정리
        temp_path = os.path.join(os.environ.get('TEMP', ''), 'scoped_dir*')
        os.system(f'del /q /s {temp_path} > nul 2>&1')

        time.sleep(2)
    except Exception as e:
        print(f"cleanup_chrome 중 오류: {e}")
# 처음에 로그인하면 되긴한다
cleanup_chrome()
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
chrome_options.add_argument("user-data-dir=C:\\NaS")  # 자신의 Chrome 프로필 경로를 지정
chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자신의 Chrome 프로필 경로를 지정

#chrome_options.add_argument("--headless")  # 디버깅을 위해 헤드리스 모드 비활성화 브라우저 띄우지않는옵션


chrome_options.add_experimental_option('detach',True)
chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])


driver = webdriver.Chrome(options=chrome_options)
driver.get("https://google.com") #한번 셀레니움켜서 로그인하면 구글유지

driver.get("https://kr.tradingview.com/chart/YsoP4fau/?symbol=BINANCE%3ABTCUSDT.P")

wait = WebDriverWait(driver, 3)  # 최대 10초 대기


xpath = "/html/body/div[2]/div[3]/div/div/div[3]/div[1]/div/div/div/div/div[4]/div/button/div"
# Wait for element to be clickable (maximum 10 seconds)




next_button = wait.until(
    EC.visibility_of_element_located(
        (By.XPATH, xpath))
)
next_button.click()

# 2. 요소 클릭
xpath = "/html/body/div[5]/div[2]/span/div[1]/div/div/div/div[30]/div"
#xpath = "/html/body/div[5]/div[2]/span/div[1]/div/div/div/div[31]/div"

# # 요소가 클릭 가능할 때까지 대기 (최대 10초)
# element = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, xpath))
# )



next_button = wait.until(
    EC.visibility_of_element_located(
        (By.XPATH, xpath))
)
next_button.click()

# 3. 스크린샷 저장
# 스크린샷 저장할 디렉토리 생성
screenshot_dir = "screenshots"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# 현재 시간을 파일명에 포함
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")

# 스크린샷 찍기
driver.save_screenshot(screenshot_path)
print(f"스크린샷 저장 완료: {screenshot_path}")


def press_shift_f(driver):
    """
    Shift + F 키 조합을 입력하는 여러 가지 방법
    """

    # 방법 1: ActionChains 사용
    try:
        actions = ActionChains(driver)
        actions.key_down(Keys.SHIFT) \
            .send_keys('f') \
            .key_up(Keys.SHIFT) \
            .perform()
        print("방법 1 성공: ActionChains로 Shift+F 입력 완료")

    except Exception as e:
        print(f"방법 1 실패: {str(e)}")

        # 방법 2: 직접 조합 전송
        try:
            active_element = driver.switch_to.active_element
            active_element.send_keys(Keys.SHIFT + 'F')
            print("방법 2 성공: 직접 키 조합 전송으로 Shift+F 입력 완료")

        except Exception as e:
            print(f"방법 2 실패: {str(e)}")

            # 방법 3: pyautogui 사용 (웹 드라이버 외부 입력)
            try:
                import pyautogui
                pyautogui.hotkey('shift', 'f')
                print("방법 3 성공: pyautogui로 Shift+F 입력 완료")

            except Exception as e:
                print(f"모든 방법 실패: {str(e)}")

import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# press_shift_f(driver)
def capture_and_encode_screenshot(driver):
    try:
        # 스크린샷 캡처
        png = driver.get_screenshot_as_png()

        # PIL Image로 변환
        img = Image.open(io.BytesIO(png))

        # 이미지 리사이즈 (OpenAI API 제한에 맞춤)
        img.thumbnail((2000, 2000))

        # 현재 시간을 파일명에 포함
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upbit_chart_{current_time}.png"

        # 현재 스크립트의 경로를 가져옴
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 파일 저장 경로 설정
        file_path = os.path.join(script_dir, filename)

        # 이미지 파일로 저장
        img.save(file_path)
        logger.info(f"스크린샷이 저장되었습니다: {file_path}")

        # 이미지를 바이트로 변환
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")

        # base64로 인코딩
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return base64_image, file_path
    except Exception as e:
        logger.error(f"스크린샷 캡처 및 인코딩 중 오류 발생: {e}")
        return None, None



import os
from dotenv import load_dotenv
import pyupbit
import pandas as pd
import json
import time
import requests
from ta.utils import dropna
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from openai import OpenAI

# Load environment variables
load_dotenv()

# API keys for Upbit and SerpAPI
access = os.environ.get("UPBIT_ACCESS_KEY")
secret = os.environ.get("UPBIT_SECRET_KEY")
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")

upbit = pyupbit.Upbit(access, secret)

# Fear and Greed Index API endpoint
fng_api_url = "https://api.alternative.me/fng/?limit=1"


def get_fear_and_greed_index():
    try:
        # Get the latest Fear and Greed Index data
        response = requests.get(fng_api_url)
        data = response.json()

        # Extract value and classification
        fng_value = int(data['data'][0]['value'])
        fng_classification = data['data'][0]['value_classification']

        return fng_value, fng_classification
    except Exception as e:
        print(f"Error fetching Fear and Greed Index: {e}")
        return None, None


# Google News API endpoint
serpapi_url = "https://serpapi.com/search"


def get_latest_news_headlines(query="Bitcoin"):
    try:
        params = {
            "engine": "google_news",
            "q": query,
            "gl": "us",
            "hl": "en",
            "api_key": serpapi_api_key
        }
        response = requests.get(serpapi_url, params=params)
        news_data = response.json()

        # Extract top headlines and dates
        news_results = news_data.get('news_results', [])
        headlines = [(news['title'], news['date']) for news in news_results]
        return headlines[:5]  # Return the top 5 news headlines with titles and dates
    except Exception as e:
        print(f"Error fetching news headlines: {e}")
        return []

import ta


def add_indicators(df):
    # 볼린저 밴드
    indicator_bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()

    # MACD
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()

    # 이동평균선
    df['sma_20'] = ta.trend.SMAIndicator(close=df['close'], window=20).sma_indicator()
    df['ema_12'] = ta.trend.EMAIndicator(close=df['close'], window=12).ema_indicator()

    return df


def get_bitcoin_news():
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_news",
        "q": "btc",
        "api_key": serpapi_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        news_results = data.get("news_results", [])
        headlines = []
        for item in news_results:
            headlines.append({
                "title": item.get("title", ""),
                "date": item.get("date", "")
            })

        return headlines[:5]
    except requests.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return []


def get_combined_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        combined_text = ' '.join(entry['text'] for entry in transcript)
        return combined_text
    except Exception as e:
        logger.error(f"Error fetching YouTube transcript: {e}")
        return ""

def ai_trading(driver):
    # Upbit 객체 생성
    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access, secret)

    # 1. 현재 투자 상태 조회
    all_balances = upbit.get_balances()
    filtered_balances = [balance for balance in all_balances if balance['currency'] in ['BTC', 'KRW']]

    # 2. 오더북(호가 데이터) 조회
    orderbook = pyupbit.get_orderbook("KRW-BTC")

    # 3. 차트 데이터 조회 및 보조지표 추가
    df_daily = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=30)
    df_daily = dropna(df_daily)
    df_daily = add_indicators(df_daily)

    df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
    df_hourly = dropna(df_hourly)
    df_hourly = add_indicators(df_hourly)

    # 4. 공포 탐욕 지수 가져오기
    fear_greed_index = get_fear_and_greed_index()

    # 5. 뉴스 헤드라인 가져오기
    news_headlines = get_bitcoin_news()

    # 6. YouTube 자막 데이터 가져오기
    youtube_transcript = get_combined_transcript("TWINrTppUl4")  # 여기에 실제 비트코인 관련 YouTube 영상 ID를 넣으세요
    # https://www.youtube.com/watch?v=4ZyPg-NkYL8&list=PLU9-uwewPMe0LLUQrBm9vfS62Jkju_rpU&index=11


    # Selenium으로 차트 캡처
    try:
        # driver = create_driver()
        # driver.get("https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC")
        # logger.info("페이지 로드 완료")
        # time.sleep(30)  # 페이지 로딩 대기 시간 증가
        # logger.info("차트 작업 시작")
        # perform_chart_actions(driver)
        logger.info("차트 작업 완료")
        chart_image, saved_file_path = capture_and_encode_screenshot(driver)
        logger.info(f"스크린샷 캡처 완료. 저장된 파일 경로: {saved_file_path}")
    # except WebDriverException as e:
    #     logger.error(f"WebDriver 오류 발생: {e}")
    #     chart_image, saved_file_path = None, None
    except Exception as e:
        logger.error(f"차트 캡처 중 오류 발생: {e}")
        chart_image, saved_file_path = None, None
    finally:
        if driver:
            driver.quit()

    # AI에게 데이터 제공하고 판단 받기
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an expert in Bitcoin investing. Analyze the provided data including technical indicators, market data, recent news headlines, the Fear and Greed Index, and the chart image. Tell me whether to buy, sell, or hold at the moment. Consider the following in your analysis:
        - Technical indicators and market data
        - Recent news headlines and their potential impact on Bitcoin price
        - The Fear and Greed Index and its implications
        - Overall market sentiment
        - The patterns and trends visible in the chart image

        Response in json format.

        Response Example:
        {"decision": "buy", "reason": "some technical, fundamental, and sentiment-based reason"}
        {"decision": "sell", "reason": "some technical, fundamental, and sentiment-based reason"}
        {"decision": "hold", "reason": "some technical, fundamental, and sentiment-based reason"}"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Current investment status: {json.dumps(filtered_balances)}
Orderbook: {json.dumps(orderbook)}
Daily OHLCV with indicators (30 days): {df_daily.to_json()}
Hourly OHLCV with indicators (24 hours): {df_hourly.to_json()}
Recent news headlines: {json.dumps(news_headlines)}
Fear and Greed Index: {json.dumps(fear_greed_index)}
YouTube Video Transcript: {youtube_transcript}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{chart_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300,
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)

    print("### AI Decision: ", result["decision"].upper(), "###")
    print(f"### Reason: {result['reason']} ###")

    if result["decision"] == "buy":
        my_krw = upbit.get_balance("KRW")
        if my_krw * 0.9995 > 5000:
            print("### Buy Order Executed ###")
            #print(upbit.buy_market_order("KRW-BTC", my_krw * 0.9995))
        else:
            print("### Buy Order Failed: Insufficient KRW (less than 5000 KRW) ###")
    elif result["decision"] == "sell":
        my_btc = upbit.get_balance("KRW-BTC")
        current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
        if my_btc * current_price > 5000:
            print("### Sell Order Executed ###")
            #print(upbit.sell_market_order("KRW-BTC", my_btc))
        else:
            print("### Sell Order Failed: Insufficient BTC (less than 5000 KRW worth) ###")
    elif result["decision"] == "hold":
        print("### Hold Position ###")


ai_trading(driver)