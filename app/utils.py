import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY") or "6ZI3IFPGYW0GD002"  
DATA_DIR = "data"  

def fetch_and_save_stock_data(symbol, time_series="TIME_SERIES_DAILY"):
    """Fetch stock data from Alpha Vantage API and save it as a JSON file."""
    function_map = {
        "TIME_SERIES_DAILY": "TIME_SERIES_DAILY",
        "TIME_SERIES_WEEKLY": "TIME_SERIES_WEEKLY",
        "TIME_SERIES_MONTHLY": "TIME_SERIES_MONTHLY"
    }

    url = f"https://www.alphavantage.co/query?function={function_map[time_series]}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Error Message" in data or not any("Time Series" in k for k in data.keys()):
        raise ValueError("Invalid API response or stock symbol")

    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    filename = os.path.join(DATA_DIR, f"{symbol}_{time_series}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return filename


def load_stock_data_from_json(symbol, time_series="TIME_SERIES_DAILY"):
    """Load stock data from a JSON file."""
    filename = os.path.join(DATA_DIR, f"{symbol}_{time_series}.json")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"No data found for {symbol} in {time_series}")

    with open(filename, "r") as f:
        data = json.load(f)

   
    time_series_key = next(k for k in data.keys() if "Time Series" in k)
    df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
    df = df.rename(columns=lambda x: x.split(". ")[1].capitalize())
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def filter_date_range(df, start_date, end_date):
    """Filter DataFrame by date range."""
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]
    return df


def generate_chart(df, chart_type, symbol):
    chart_filename = f"{symbol}_{chart_type}.png"
    chart_dir = os.path.join("static", "charts")
    os.makedirs(chart_dir, exist_ok=True)  

    chart_path = os.path.join(chart_dir, chart_filename)

    
    plt.clf()

 
    try:
        if chart_type == 'line':
            df['Close'].plot(title=f"{symbol} Closing Prices")
            plt.xlabel('Date')
            plt.ylabel('Price')
        elif chart_type == 'bar':
            df['Close'].plot(kind='bar', title=f"{symbol} Closing Prices")
            plt.xlabel('Date')
            plt.ylabel('Price')
        else:
            raise ValueError("Unsupported chart type")

    except KeyError as e:
        print(f"Error: {e}. The column 'Close' is not found in the data.")
        raise

    plt.tight_layout()

   
    print(f"Saving chart to: {chart_path}")  

    plt.savefig(chart_path)
    plt.close()

    return chart_filename


    try:
        if chart_type == 'line':
            # Use the correct column name for '4. close'
            df['Close'].plot(title=f"{symbol} Closing Prices")
            plt.xlabel('Date')
            plt.ylabel('Price')
        elif chart_type == 'bar':
            df['Close'].plot(kind='bar', title=f"{symbol} Closing Prices")
            plt.xlabel('Date')
            plt.ylabel('Price')
        else:
            raise ValueError("Unsupported chart type")

    except KeyError as e:
        print(f"Error: {e}. The column '4.close' is not found in the data.")
        raise

    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_filename


def generate_table_html(df):
    """Generate HTML table from DataFrame."""
    return df.to_html(classes="table table-striped", border=0)
