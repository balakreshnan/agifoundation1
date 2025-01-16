import yfinance as yf
import pandas as pd

def fetch_tesla_stock_data():
    # Define the ticker symbol for Tesla
    ticker_symbol = 'TSLA'
    
    # Fetch the data for the last 6 months
    tesla_data = yf.Ticker(ticker_symbol)
    stock_data = tesla_data.history(period='6mo')
    
    # Print the data as a table
    print(stock_data)
    
    # Save the data to a CSV file
    stock_data.to_csv('stocks.csv')

# Call the function
fetch_tesla_stock_data()