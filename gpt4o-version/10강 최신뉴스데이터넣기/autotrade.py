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


# 24시간마다 실행
while True:
    ai_trading()
    time.sleep(3600 * 24)
