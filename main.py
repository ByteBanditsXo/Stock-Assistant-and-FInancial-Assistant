import json
from numpy import append
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf

openai.api_key = open('API_KEY','r').read()

#Function to get Stock price
def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period = '1y').iloc[-1].close)

#Function for calculate Simple Moving Average
'''It is simply the average price over the specified period.'''
def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period = '1y').Close
    return str(data.rolling(window=window).mean().iloc[-1])

#Function for Exponential Moving Average (EMA)
'''is a kind of moving average that places a greater weight and importance on 
   the most current data points.'''
def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period = '1y').Close
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1])

#Function for Relative Strength Index (RSI)
'''It is a momentum oscillator that measures the speed and change of price movements.'''
def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period = '1y').Close
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com = 14-1, adjust=False).mean()
    ema_down = down.ewm(com = 14-1, adjust=False).mean()
    rs = ema_up/ema_down
    return str(100 - (100/(1+rs)).iloc[-1])

#Function for Moving Average Convergence/Divergence (MACD)
'''It is a technical indicator to help investors identify market entry 
   points for buying or selling.'''
def calculate_MACD(ticker):
     data = yf.Ticker(ticker).history(period = '1y').Close
     short_EMA = data.ewm(span = 12, adjust=False).mean()
     long_EMA = data.ewm(span = 26, adjust=False).mean()
     
     MACD = short_EMA - long_EMA
     signal = MACD.ewm(span=9, adjust=False).mean()
     MACD_histogram = MACD - signal 
     
     return f'{MACD[-1]}, {signal[-1]}, {MACD_histogram[-1]}'
 
#Calculating Market Capitalization
'''Market capitalization (market cap) is the total value of a company's stock, 
   which is calculated by multiplying the current market price of a 
   company's shares by the total number of outstanding shares.'''
def calculate_market_cap(ticker):
    data = yf.Ticker(ticker).history(period = '1y').Close
    stock = yf.Ticker(ticker)
    market_price = stock.history(period='1d').Close[-1]
    outstanding_shares = stock.info['sharesOutstanding']
    
    market_cap = market_price * outstanding_shares
    
    return f'The market capitalization of {ticker} is {market_cap:.2f}'

#Plotting the Stock Price
def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period = '1y')
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.Close)
    plt.title('{ticker} Stock PRICE OVER LAST YEAR')
    plt.xlabel('Date')
    plt.ylabel('Stock Price ($)')
    plt.grid(True)
    plt.savefig('stock.png')
    plt.close()
    
functions =[
    {
        'name': 'get_stock_price', 
        'description': 'Gets the latest Stock Price given the ticker symbol of a company.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                }
            },
            'required': ['ticker'],
        }
    },
    {
        "name": "calculate_SMA",
        "description": "Calculate the simple moving average for a give stock ticker and window",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                },
                "window":{
                    "type": "integer",
                    "description": "The timeframe to consider when calculating simple moving average"
                }
            },
            "required": ["ticker", "window"],
        },
    },
    {
        "name": "calculate_EMA",
        "description": "Calculate the exponential moving average for a given stock ticker and window",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                },
                "window":{
                    "type": "integer",
                    "description": "The timeframe to consider when calculating exponential moving average"
                },
            },
            "required": ["ticker", "window"],
        },
    },
    {
        "name": "calculate_RSI",
        "description": "Calculate the relative strength index for a given stock ticker",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_MACD",
        "description": "Calculate the MACD for a given stock ticker",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_market_cap",
        "description": "Calculate the market capitalization for a given stock ticker",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "plot_stock_price",
        "description": "Plot the stock price for a given stock ticker",
        "parameters":{
            "type": "object",
            "properties":{
                "ticker":{
                    "type": "string",
                    "description": "The stock ticker symbol for a company (for example AAPL for Apple)"
                },
            },
            "required": ["ticker"],
        },
    }
]


available_functions = {
    'get_stock_price': get_stock_price,
    'calculate_SMA': calculate_SMA,
    'calculate_EMA': calculate_EMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
    'calculate_market_cap': calculate_market_cap,
    'plot_stock_price': plot_stock_price,
    
}

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
st.title('Stock Analysis and Assistant chatbot') 
user_input = st.text_input('Your input: ')   

if user_input:
    try:
        st.session_state['messages'].append({'role': 'user', 'content': f'{user_input}'})
        
        response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0613',
        messages = st.session_state["messages"],
        functions=functions,
        function_call='auto'
        
        )
        
        reponse_message = response['choices']['0']['message']
        
        if reponse_message.get('function_call'):
            function_name = reponse_message['function_call']['name']
            function_args = json.loads(reponse_message['function_call']['arguments'])
            if function_name in ['get_stock_price','calculate_RSI','calculate_MACD','calculate_market_cap']:
                args_dict = {'ticker':function_args.get('ticker')}
            elif function_name in ['calculate_SMA','calculate_EMA']:
                args_dict = {'ticker': function_args.get('ticker'), 'window': function_args.get('window')}  
                
            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)
            
            if function_name == 'plot_stock_price':
                st.Image('stock.png') # type: ignore
            else:
                st.session_state['messages'].append(reponse_message)         
                st.session_state['messages'],append(
                    {
                        'role': 'function',
                        'name': function_name,
                        'contant': function_response
                    }
                ) 
                second_response = openai.ChatCompletion.create(
                    model = 'gpt-3.5-turbo-0613',
                    messages = st.session_state['messages']
                )
                st.text(second_response['choices']['0']['message']['content'])
                st.session_state['messages'].append({'role': 'assistant', 'content': second_response['choices']['0']['message']['content']})
        else:
            st.text(reponse_message['content'])
            st.session_state['message'].append({'role': 'assistant', 'content': reponse_message['content']})      
    except:
        st.text('try again')