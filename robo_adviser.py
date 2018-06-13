import requests
import json
import os
from IPython import embed
import csv

api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "Oops! Please enter a valid key."
print(api_key)

def parse_response(response_text):

    # text will either be JSON or dictionary
    if isinstance(response_text, str):
        response_text = json.loads(response_text)

    results = []
    time_series_daily = response_text["Time Series (Daily)"]
    for trading_date in time_series_daily: #to loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date]
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="robo_adviser_prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_filepath, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for x in prices:
            row = {
                "timestamp": x["date"],
                "open": x["open"],
                "high": x["high"],
                "low": x["low"],
                "close": x["close"],
                "volume": x["volume"]
            }
            writer.writerow(row)

if __name__ == '__main__':

 # CAPTURE USER INPUT

    symbol = input("Please input a stock ticker (e.g. 'NFLX'): ")

    # VALIDATE SYMBOL
    try:
        float(symbol)
        quit("Tickers should comprise 4 letters. Please review your ticker and re-enter. Thank you.")
    except ValueError as e:
        pass

    # ASSEMBLE REQUEST URL

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    # ISSUE "GET" REQUEST
    print("Issuing a request")
    response = requests.get(request_url)

    # VALIDATE RESPONSE AND HANDLE ERRORS

    if "Error Messsage" in response.text:
        print("Tickers should comprise 4 letters. Please review your ticker and re-enter. Thank you.")
        quit("Stopping the program.")

    #Parse response

    daily_prices = parse_response(response.text)

    #write to CSV file

    write_prices_to_file(prices=daily_prices, filename="robo_adviser_prices.csv")

    # Calculation

    print("Here's some information for",symbol,":")

    print("Program was ran on:",datetime.now())

    latest_close = daily_prices[0]['close']
    latest_close = float(latest_close)
    latest_close_usd = "${0:,.2f}".format(latest_close)
    print("The last closing price for",symbol,"is:",latest_close_usd)

    date_last = daily_prices[0]['date']
    print("This data was last refreshed on:", date_last)

    # FOLLOWING ADAPTED FROM: https://stackoverflow.com/questions/5320871/in-list-of-dicts-find-min-value-of-a-common-dict-field

    last_year = daily_prices[:252]
    last_year = [x['close'] for x in last_year]

    max_last_year = float(max(last_year))
    max_last_year = "${0:,.2f}".format(max_last_year)
    print("The highest price for",symbol," in the last year is:",max_last_year)

    min_last_year = float(min(last_year))
    min_last_year = "${0:,.2f}".format(min_last_year)
    print("The lowest price for",symbol,"in the last year is:",min_last_year)

    # Recommendation
    percent_dif_high_low = (float(max(last_year))-float(min(last_year)))/float(min(last_year))
    if percent_dif_high_low >= .15:
        print("Do not buy",symbol)
    else:
        print("Buy",symbol)

    print("This recommendation is based on the percent differential from the high and low prices.",
    "If the price is greater than 15%, the recommendation is do not buy. If the price is less than 15%, the recommendation is buy")
