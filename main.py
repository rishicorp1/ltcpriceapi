from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Read proxies from proxies.txt file
def get_proxies():
    with open('proxies.txt', 'r') as file:
        proxies_list = [line.strip() for line in file.readlines()]
    return proxies_list

# Rotate proxies in a round-robin fashion
def rotate_proxies(proxies_list):
    while True:
        for proxy in proxies_list:
            yield proxy

# Create a generator for rotating proxies
proxy_generator = rotate_proxies(get_proxies())

# Toggle to use proxies or not
use_proxies = False  # Set to False if you don't want to use proxies

@app.route('/')
def get_ltc_price():
    # CoinGecko API endpoint and parameters
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'litecoin',
        'vs_currencies': 'usd',
    }

    # CoinGecko API request headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY',  # Replace with your actual API key
    }

    try:
        # Check if proxies should be used
        if use_proxies:
            # Get the next proxy from the generator
            current_proxy = next(proxy_generator)

            # Create the proxies dictionary
            proxies = {
                'http': f'http://{current_proxy}',
                'https': f'http://{current_proxy}',
            }
        else:
            # If not using proxies, set proxies to None
            proxies = None

        # Make the CoinGecko API request with the current proxy
        response = requests.get(url, params=params, headers=headers, proxies=proxies)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            ltc_price = data['litecoin']['usd']
            result = {
                'ltc_price': ltc_price,
                'current_proxy': current_proxy if use_proxies else None,
            }
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to fetch LTC price from CoinGecko API'}), 500

    except requests.RequestException as e:
        # Handle request exceptions (e.g., network error)
        return jsonify({'error': f'Request error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
