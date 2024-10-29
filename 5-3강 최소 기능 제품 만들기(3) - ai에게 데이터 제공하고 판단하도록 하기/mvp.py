import os
from dotenv import load_dotenv
load_dotenv()

# 1. 업비트 차트 데이터 가져오기 (30일 일봉)
import pyupbit


def ai_trading():
    df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You are an expert in Bitcoin investing. Tell me whether to buy, sell , or hold at the moment based on the chart data provided. response in json format\n\nResponse Example:\n{\"decision\":\"buy\", \"reason\": \"\"some technical reason\"}\n{\"decision\":\"sell\", \"reason\": \"\"some technical reason\"}\n{\"decision\":\"hold\", \"reason\": \"\"some technical reason\"}\n\n\n\n"
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": df.to_json()
            }
          ]
        }
      ],
      # temperature=1,
      # max_tokens=2048,
      # top_p=1,
      # frequency_penalty=0,
      # presence_penalty=0,
      response_format={
        "type": "json_object"
      }
    )

    import json
    result = response.choices[0].message.content
    result = json.loads(result)
    print(result['decision'])

    # 로그인
    #  https://github.com/sharebook-kr/pyupbit
    access = os.environ.get("UPBIT_ACEESS_KEY")
    secret = os.environ.get("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access,secret)


    print('### AI Decision:', result['decision'].upper(),"###")
    print(f"### Reason:'{result['reason']}")
    if result == "buy":
        # 잔고 조회
        my_krw = upbit.get_balance("KRW")
        # 잔고가 원화 기준 5000원 이상이어야함
        if my_krw * 0.9995 > 5000:
            print("### Buy Order Executed ### ")
            print(upbit.buy_market_order("KRW-BTC",my_krw * 0.9995))# 수수료만큼 빼야함 # 전액 현금 보유하려면 수수료가 고려가 안되서 거래안됨
            print("buy:",result['reason']) # 모든 잔고로 사기
        else:
            print("원화 5000원 미만")
            print("### Buy Order Failed : Insufficient KRW (less than 5000 KRW) ###")
    elif result == "hold":
        my_btc = upbit.get_balance("KRW-BTC")
        current_price = pyupbit.get_orderbook(ticker='KRW-BTC')['orderbook_units'][0]['ask_price']  #매도 호가
        if (my_btc * current_price) *0.9995 >5000: # 내 BTC의 원화 가치
            print("### Sell Order Executed ### ")
            print(upbit.sell_market_order("KRW-BTC", upbit.get_balance('KRW-BTC')))
            print("sell:",result['reason']) # 모든 잔고 팔기
            print("### Sell Order Failed : Insufficient BTC (less than 5000 KRW worth) ###")
        else:
            print("btc 5000원 미만")
    elif result=='sell':
        print("hold:",result['reason']) # 모든 잔고로 사기

#
# while True:
#     import time
#     time.sleep(3600*24)
ai_trading()


# 2. 바이낸스 차트 데이터 가져오기

# 5-5강 최소 기능 제품 만들기(5) - 디테일 수정 및 자ㄷ