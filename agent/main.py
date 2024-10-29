import os

import pandas as pd
import requests
import ta
import logger
import pyupbit

#TODO: 카카오톡 대화 데이터 가져오기
load_dotenv()

# 데이터프레임의 종가 가격으로 주식 볼린저 밴드 계산하기
df = get_bollinger_band(df)


def get_bollinger_band(df) -> pd.DataFrame:
    indicator_bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()
    return df
# 데이터프레임의 종가 가격으로 RSI 계산하기
def get_rsi(df):
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    return df
 # MACD
def get_macd(df):
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    return df
# 비트코인 공포탐욕지수 데이터 가져오기
def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data'][0]
    else:
        logger.error(f"Failed to fetch Fear and Greed Index. Status code: {response.status_code}")
        return None


# 비트코인 뉴스데이터 가져오기
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


def ai_trading():
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
    # 30일 일봉 데이터
    df_daily = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=30)

    # 24시간 시간봉 데이터
    df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)

    # AI에게 데이터 제공하고 판단 받기
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """You are an expert in Bitcoin investing. Analyze the provided data including technical indicators and tell me whether to buy, sell, or hold at the moment. Consider the following indicators in your analysis:
        - Bollinger Bands (bb_bbm, bb_bbh, bb_bbl)
        - RSI (rsi)
        - MACD (macd, macd_signal, macd_diff)
        - Moving Averages (sma_20, ema_12)

        Response in json format.

        Response Example:
        {"decision": "buy", "reason": "some technical reason"}
        {"decision": "sell", "reason": "some technical reason"}
        {"decision": "hold", "reason": "some technical reason"}"""
            },
            {
                "role": "user",
                "content": f"Current investment status: {json.dumps(filtered_balances)}\nOrderbook: {json.dumps(orderbook)}\nDaily OHLCV with indicators (30 days): {df_daily.to_json()}\nHourly OHLCV with indicators (24 hours): {df_hourly.to_json()}"
            }
        ],
        response_format={
            "type": "json_object"
        }
    )
    result = response.choices[0].message.content

    # AI의 판단에 따라 실제로 자동매매 진행하기
    result = json.loads(result)

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



# 많은 데이터를 뿌려놓고 특성 이해하기
# 볼린저 밴드


# 학습 목적에 맞게 변형하기
# 모델 선택하기

model_selection



client = OpenAI()

# 에이전트 만들기
# 테스트 및 검증하기
# 개선하기


if __name__ == '__main__':
    # 모델 설정하기
    model = OpenAI()
    # 업비트 현물 매수매도 에이전트 생성하기
    upbit_agent = get_upbit_trader(model)

    #     # 일목균형표의 이격도와 현재 시장 상황,  이전에 저항대를 한번 뚫으면 뚫는 패턴 등을 인식하도록 하기
    # 사람들의 질문을찾거나 직접사람들한테질문을던져서 수요조사
    # 어떤 etf를 원하시는ㄷ지 어떤 ai가 있었으면 좋겠는지
    # 보유기간에 비해 급등했따싶으면 매도하는로직
