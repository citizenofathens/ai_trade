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

from openai import OpenAI

# 로그인 정보 설정
# xpath로 이동할수있는요소를 정확히클릭해야함
import os
from datetime import datetime
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
import logger

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


def ai_trading():
    try:
        # 1. 업비트에서 일봉과 시간봉 데이터 가져오기
        df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')  # 30일 일봉 데이터
        df_hourly = pyupbit.get_ohlcv("KRW-BTC", count=24, interval='minute60')  # 24시간 시간봉 데이터

        # 2. NaN 값 제거
        df_daily = dropna(df_daily)
        df_hourly = dropna(df_hourly)

        # 3.1 일봉 데이터에 Bollinger Bands 및 RSI 추가
        bb_daily = BollingerBands(close=df_daily['close'], window=20, window_dev=2)
        df_daily['bb_mavg'] = bb_daily.bollinger_mavg()
        df_daily['bb_hband'] = bb_daily.bollinger_hband()
        df_daily['bb_lband'] = bb_daily.bollinger_lband()

        rsi_daily = RSIIndicator(close=df_daily['close'], window=14)
        df_daily['rsi'] = rsi_daily.rsi()

        # 3.2 시간봉 데이터에 Bollinger Bands 및 RSI 추가
        bb_hourly = BollingerBands(close=df_hourly['close'], window=20, window_dev=2)
        df_hourly['bb_mavg'] = bb_hourly.bollinger_mavg()
        df_hourly['bb_hband'] = bb_hourly.bollinger_hband()
        df_hourly['bb_lband'] = bb_hourly.bollinger_lband()

        rsi_hourly = RSIIndicator(close=df_hourly['close'], window=14)
        df_hourly['rsi'] = rsi_hourly.rsi()

        # Timestamp를 문자열로 변환
        df_daily.index = df_daily.index.strftime('%Y-%m-%d %H:%M:%S')
        df_hourly.index = df_hourly.index.strftime('%Y-%m-%d %H:%M:%S')

        # 4. 공포와 탐욕 지수 가져오기
        fng_value, fng_classification = get_fear_and_greed_index()
        if fng_value is None:
            print("공포와 탐욕 지수를 가져오지 못했습니다. 기본 판단을 진행합니다.")
            fng_classification = "Neutral"  # 기본 값 설정

        print(f"### Fear and Greed Index: {fng_value} ({fng_classification}) ###")

        # 5. 최신 뉴스 헤드라인 가져오기
        headlines = get_latest_news_headlines(query="Bitcoin")
        if headlines:
            print("### Latest News Headlines ###")
            for idx, (title, date) in enumerate(headlines, 1):
                print(f"{idx}. {title} - {date}")


        # 6. AI 트레이딩 로직
        client = OpenAI()



        # 보조지표와 함께 AI에게 데이터를 전달
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in Bitcoin investing. "
                        "Tell me whether to buy, sell, or hold at the moment based on the technical indicators, Fear and Greed Index, news headlines, and chart data provided. "
                        "Response in json format. \n\n"
                        "Response Example:\n"
                        "{\"decision\":\"buy\", \"reason\": \"some technical reason\"}\n"
                        "{\"decision\":\"sell\", \"reason\": \"some technical reason\"}\n"
                        "{\"decision\":\"hold\", \"reason\": \"some technical reason\"}\n"
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "30_day_ohlcv": df_daily[['close', 'bb_mavg', 'bb_hband', 'bb_lband', 'rsi']].to_dict(),
                        "24h_ohlcv": df_hourly[['close', 'bb_mavg', 'bb_hband', 'bb_lband', 'rsi']].to_dict(),
                        "fear_and_greed_index": {
                            "value": fng_value,
                            "classification": fng_classification
                        },
                        "latest_news": headlines
                    })
                }
            ],
            response_format={"type": "json_object"}
        )

        # AI 응답 처리
        result = response.choices[0].message.content
        result = json.loads(result)
        decision = result['decision']
        reason = result['reason']

        print('### AI Decision:', decision.upper(), "###")
        print(f"### Reason: '{reason}' ###")

        # 매수/매도/보유 로직 실행
        if decision == "buy":
            # 원화 잔고 확인 후 매수
            my_krw = upbit.get_balance("KRW")
            if my_krw * 0.9995 > 5000:
                print("### Buy Order Executed ###")
                print(upbit.buy_market_order("KRW-BTC", my_krw * 0.9995))
            else:
                print("원화 잔고 부족 (5000 KRW 미만)")
        elif decision == "sell":
            my_btc = upbit.get_balance("KRW-BTC")
            if my_btc * pyupbit.get_current_price("KRW-BTC") > 5000:
                print("### Sell Order Executed ###")
                print(upbit.sell_market_order("KRW-BTC", my_btc))
            else:
                print("비트코인 잔고 부족 (5000 KRW 미만)")
        elif decision == "hold":
            print("### Holding Position ###")

    except pyupbit.errors.RemainingReqParsingError as e:
        print("API 요청 제한 오류가 발생했습니다. 잠시 후 다시 시도합니다.")
        time.sleep(60)  # 1분 대기 후 다시 시도
        ai_trading()  # 재시도

    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        time.sleep(60)  # 1분 대기 후 다시 시도
        ai_trading()  # 재시도




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
Fear and Greed Index: {json.dumps(fear_greed_index)}"""
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
        print(upbit.buy_market_order("KRW-BTC", my_krw * 0.9995))
    else:
        print("### Buy Order Failed: Insufficient KRW (less than 5000 KRW) ###")
elif result["decision"] == "sell":
    my_btc = upbit.get_balance("KRW-BTC")
    current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
    if my_btc * current_price > 5000:
        print("### Sell Order Executed ###")
        print(upbit.sell_market_order("KRW-BTC", my_btc))
    else:
        print("### Sell Order Failed: Insufficient BTC (less than 5000 KRW worth) ###")
elif result["decision"] == "hold":
    print("### Hold Position ###")