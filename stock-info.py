from flask import Flask, request, render_template
import requests
from dotenv import load_dotenv
import os
import datetime

app = Flask(__name__)

def get_stock_data(symbol):
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    base_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    base_url_name = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an error for HTTP status codes indicating failure
        response_name = requests.get(base_url_name)
        response_name.raise_for_status()  # Raise an error for HTTP status codes indicating failure

        data = response.json()
        data_name = response_name.json()

        if 'Global Quote' in data and 'Name' in data_name:
            stock_data = data['Global Quote']
            name = data_name['Name']
            return {
                "symbol": stock_data["01. symbol"],
                "price": float(stock_data["05. price"]),
                "company_name": name,
                "change": float(stock_data["09. change"]),
                "percent_change": stock_data["10. change percent"],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return None

    except requests.exceptions.HTTPError as err:
        # Handle HTTP errors (e.g., 404, 500)
        print(f"HTTP error occurred: {err}")
        return None

    except requests.exceptions.RequestException as err:
        # Handle network-related errors
        print(f"Network error occurred: {err}")
        return None

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/stock', methods=['POST'])
def stock():
    data = request.form
    stock_data = get_stock_data(data['symbol'].upper())
    if stock_data:
        return render_template('stock.html', stock=stock_data)
    else:
        return f"Could not fetch data for symbol: {data['symbol'].upper()}, Check the symbol and try again."

if __name__ == "__main__":
    app.run(debug=True)
