import os
from dotenv import load_dotenv
import pyupbit
import json
import time

# Load environment variables
load_dotenv()

# API keys for Upbit
access = os.environ.get("UPBIT_ACCESS_KEY")
secret = os.environ.get("UPBIT_SECRET_KEY")
upbit = pyupbit.Upbit(access, secret)


python
코드 복사
import pyupbit
import pandas as pd
from ta.utils import dropna
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

# 1. 업비트에서 일봉과 시간봉 데이터 가져오기
df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')  # 30일 일봉 데이터
df_hourly = pyupbit.get_ohlcv("KRW-BTC", count=24, interval='minute60')  # 24시간 시간봉 데이터

print("일봉 데이터:")
print(df_daily.head())

print("\n시간봉 데이터:")
print(df_hourly.head())

# 2. NaN 값 제거
df_daily = dropna(df_daily)
df_hourly = dropna(df_hourly)


def ai_trading():
    try:
        # 1. 현재 투자 상태(잔고)
        print("### Current Investment Status ###")
        balance = upbit.get_balances()
        print(balance)

        # 2. 호가 데이터 가져오기
        print("### Orderbook Data (KRW-BTC) ###")
        orderbook = pyupbit.get_orderbook(ticker="KRW-BTC")
        print(orderbook)

        # 3. 차트 데이터 가져오기 (30일 일봉, 24시간 시간봉)
        print("### 30-day Daily OHLCV Data ###")
        df_30d = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')

        # Timestamp를 문자열로 변환
        df_30d.index = df_30d.index.strftime('%Y-%m-%d %H:%M:%S')
        print(df_30d)

        print("### 24-hour Timeframe OHLCV Data ###")
        df_24h = pyupbit.get_ohlcv("KRW-BTC", count=1, interval='minute240')

        # Timestamp를 문자열로 변환
        df_24h.index = df_24h.index.strftime('%Y-%m-%d %H:%M:%S')
        print(df_24h)

        # AI 트레이딩 로직
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in Bitcoin investing. "
                        "Tell me whether to buy, sell, or hold at the moment based on the chart data provided. "
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
                        "30_day_ohlcv": df_30d.to_dict(),
                        "24h_ohlcv": df_24h.to_dict(),
                        "orderbook": orderbook,
                        "balance": balance
                    })
                }
            ],
            response_format={"type": "json_object"}
        )

        # Process the AI's response
        result = response.choices[0].message.content
        result = json.loads(result)
        print(result['decision'])

        # 매수/매도/보유 로직 실행
        decision = result['decision']
        reason = result['reason']

        print('### AI Decision:', decision.upper(), "###")
        print(f"### Reason: '{reason}' ###")

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
#while True:
ai_trading()
 #   time.sleep(3600 * 24)
