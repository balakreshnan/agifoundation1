import openai

print(openai.__version__)

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_tesla_stock_data():
    # Define the ticker symbol for Tesla
    ticker_symbol = 'TSLA' 
    # Calculate the date range for the last 6 months\n    
    end_date = datetime.now()    
    start_date = end_date - timedelta(days=6*30)  
    # Approximate 6 months as 180 days\n    \n    
    # # Fetch the stock data using yfinance\n    
    tesla_data = yf.download(ticker_symbol, start=start_date, end=end_date)    
    # Print the data as a table\n    
    print(tesla_data)   
    # Save the data to a CSV file\n    
    tesla_data.to_csv('stocks.csv')
    # Call the function to fetch and display the data\n
    # 
fetch_tesla_stock_data()