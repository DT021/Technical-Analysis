import urllib, urllib.parse, urllib.error, urllib.request
import ssl
import json
from datetime import datetime
from pytz import timezone

tz = timezone('EST')

import pprint

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# THe ConnorsRSI combines three composite components: price momentum, duration of up/down trend

# robinhood_100_most_popular = ('ACB', 'F', 'GE', 'GPRO', 'FIT' 'AAPL', 'DIS', 'SNAP', 'MSFT', 'TSLA', 'AMZN', 'FB', 'GOOGL', 'NVDA', 'INTC', 'BABA', 'UBER', 'BAC', 'T', 'SBUX')
# vix = 'VIX'
tesla_ticker = 'DIS'

def price_change (ticker):
    url_rsi = 'https://www.alphavantage.co/query?' + urllib.parse.urlencode({'interval':'daily', 'function': 'RSI', 'time_period':'3', 'series_type':'close', 'symbol': ticker, 'apikey': '2VNO5H70PQ6GSC98'})   
    pre_json_rsi = urllib.request.urlopen(url_rsi, context = ctx).read().decode()
    loaded_json_rsi = json.loads(pre_json_rsi)['Technical Analysis: RSI'].values()

    return float(list(loaded_json_rsi).pop(0)['RSI'])

#Applying the RSI formula to the duration_of_trend as opposed to close values
def duration_of_trend (ticker):
    prices = []
    
    url_prices = 'https://www.alphavantage.co/query?' + urllib.parse.urlencode({'interval': 'daily', 'outputsize': 'compact', 'function':'TIME_SERIES_DAILY', 'symbol': ticker, 'apikey': 'IXV1N1AE5OTCW4KR'})   
    pre_json_prices = urllib.request.urlopen(url_prices, context = ctx).read().decode()
    loaded_json_prices = json.loads(pre_json_prices)['Time Series (Daily)'].values()

    for price in loaded_json_prices : 
        prices.append(float(price['4. close']))

    streak = 0
    streaks = []

    for index in reversed(range(0, len(prices) - 1)) : 
        if (prices[index] > prices[index+1]) :
            if (streak < 0) : streak = 0
            streak += 1
            streaks.append(streak)
        elif (prices[index] < prices[index+1]) : 
            if (streak > 0) : streak = 0
            streak -= 1
            streaks.append(streak)
        else :
            streak = 0
            streaks.append(streak)
            
    streaks.reverse()
    upwards_movement = []
    downwards_movement = []

    for index in reversed(range(0, len(streaks)-1)) : 
        if (streaks[index] - streaks[index+1] >= 0 ) :
            upwards_movement.append(streaks[index] - streaks[index+1])
            downwards_movement.append(0)
        elif ((streaks[index] - streaks[index+1] < 0 )) :
            upwards_movement.append(0)
            downwards_movement.append(abs(streaks[index] - streaks[index+1]))

    upwards_movement.reverse()
    downwards_movement.reverse()

    average_upwards_movement = [(upwards_movement[-2] + upwards_movement[-1]) / 2]
    average_downwards_movement = [(downwards_movement[-2] + downwards_movement[-1]) / 2]

    for index in reversed(range(0, len(upwards_movement) - 2)) :
        average_upwards_movement.append((average_upwards_movement[-1] * 1 + upwards_movement[index]) / 2)
        average_downwards_movement.append((average_downwards_movement[-1] * 1 + downwards_movement[index]) / 2)

    average_upwards_movement.reverse()
    average_downwards_movement.reverse()

    relative_strength_indices = []

    for index in reversed(range(0, len(average_upwards_movement))) :
        relative_strength_indices.append(100 - 100/(average_upwards_movement[index] / average_downwards_movement[index] + 1))
    
    relative_strength_indices.reverse()
    return relative_strength_indices.pop(1)

def relative_magnitude_price_change (ticker):
    prices = []
    
    url_prices = 'https://www.alphavantage.co/query?' + urllib.parse.urlencode({'interval': 'daily', 'outputsize': 'compact', 'function':'TIME_SERIES_DAILY', 'symbol': ticker, 'apikey': 'IXV1N1AE5OTCW4KR'})   
    pre_json_prices = urllib.request.urlopen(url_prices, context = ctx).read().decode()
    loaded_json_prices = json.loads(pre_json_prices)['Time Series (Daily)'].values()
    
    for price in loaded_json_prices : 
        prices.append(float(price['4. close']))

    percent_rank = 0
    previous_day_price = prices.pop(0)
    previous_day_return = (previous_day_price - prices[0])/previous_day_price

    for index in range(0, len(prices) - 1) : 
        price_change = (prices[index] - prices[index+1])/prices[index]
        if (previous_day_return > price_change) : percent_rank += 1

    return percent_rank / 98 * 100

def two_period_rsi (ticker) : 
    official_rsi = (price_change(tesla_ticker) + duration_of_trend(tesla_ticker) + relative_magnitude_price_change(tesla_ticker)) / 3
    return official_rsi

    # if (official_rsi >= 90) : 
    #     return ('(' + str(datetime.now(tz)) + ') ' + ticker + ' overbought')
    # elif (official_rsi <= 10) : 
    #     return ('(' + str(datetime.now(tz)) + ') ' + ticker + ' oversold')
    # else : 
    #     return ('(' + str(datetime.now(tz)) + ') ' + ticker + ' stable') 

print(two_period_rsi(tesla_ticker))
