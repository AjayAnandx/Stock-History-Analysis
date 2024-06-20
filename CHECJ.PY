import yfinance as yf
import pandas as pd
import requests
import json
import time

def get_ticker_symbol(company_name, api_key):
    search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={api_key}"

    response = requests.get(search_url)

    if response.status_code == 200:
        try:
            data = json.loads(response.text)
            if 'bestMatches' in data and len(data['bestMatches']) > 0:
                ticker_symbol = data['bestMatches'][0]['1. symbol']
                return ticker_symbol
            else:
                print("No matching ticker found.")
                return None
        except Exception as e:
            print(f"An error occurred while parsing the JSON data: {e}")
            return None
    else:
        print(f"Request failed with status code {response.status_code}")
        return None

def get_stock_data(ticker_symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker_symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data["Global Quote"]

def update_stock_live(ticker_symbol, api_key, refresh_interval=30):
    while True:
        stock_data = get_stock_data(ticker_symbol, api_key)

        if stock_data:
            last_price = stock_data.get("05. price", None)
            previous_close = stock_data.get("08. previous close", None)
            day_range = f"{stock_data.get('02. high', 'N/A')} - {stock_data.get('03. low', 'N/A')}"
            volume = stock_data.get("06. volume", None)

            print(f"Live Stock Data for {ticker_symbol}:")
            print(f"Last Price: {last_price}")
            print(f"Previous Close: {previous_close}")
            print(f"Day Range: {day_range}")
            print(f"Volume: {volume}")
            print("-"*30)
        else:
            print(f"No data available for {ticker_symbol} at this time.")

        time.sleep(refresh_interval)

def analyze_stock(ticker_symbol):
    # Download historical data as dataframe
    data = yf.download(ticker_symbol, start='2020-01-01', end=pd.Timestamp.now().strftime('%Y-%m-%d'))

    # Calculate daily percentage change
    data['Daily Returns'] = data['Adj Close'].pct_change()

    # Calculate average daily volume
    average_volume = data['Volume'].mean()

    # Calculate stock volatility
    stock_volatility = data['Daily Returns'].std()

    # Calculate moving averages
    data['100ma'] = data['Adj Close'].rolling(window=100).mean()
    data['200ma'] = data['Adj Close'].rolling(window=200).mean()

    print(f"Average daily volume: {average_volume:.2f}")
    print(f"Stock volatility: {stock_volatility:.2%}")

    # Plot moving averages
    import matplotlib.pyplot as plt

    plt.plot(data['Adj Close'])
    plt.plot(data['100ma'])
    plt.plot(data['200ma'])
    plt.legend(['Adj Close', '100ma', '200ma'])
    plt.show()

print("Welcome to the Stock Analysis Tool!")
company_name = input("Enter the Company Name: ")
api_key = "JBQHL6764PCI6125"
ticker_name = get_ticker_symbol(company_name, api_key)

if ticker_name:
    print(f"The ticker symbol for {company_name} is {ticker_name}")
    user_choice = input("What would you like to do? (1) Fetch live stock price (2) Perform stock analysis: ")

    if user_choice == '1':
        update_stock_live(ticker_name, api_key)
    elif user_choice == '2':
        analyze_stock(ticker_name)
    else:
        print("Invalid option. Please enter 1 or 2")
