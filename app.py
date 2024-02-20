import streamlit as st
import requests
import os
import time
from openai import OpenAI
from datetime import datetime, timezone, timedelta


# Set the title of the app
st.title('Stock News Generator')

# App description
st.write(
    "This application creates financial articles for all US stocks based on price information, time of the day and "
    "trend of the stock as input by the financial analyst")

# Input for stock symbol, converted to uppercase
symbol = st.text_input('Enter Stock Symbol').upper()

# Attempt to load API keys from environment variables
try:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    GETQUOTE_API_KEY = os.environ['GETQUOTE_API_KEY']




except KeyError as e:
    st.error(f"Environment variable {e} not set. Please check your .env file or environment configuration.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to determine the current time period in EST
def get_time_period():
    est = timezone(timedelta(hours=-5))  # EST timezone
    now_est = datetime.now(est)
    pre_market_start = now_est.replace(hour=4, minute=15, second=0, microsecond=0)
    market_start = now_est.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now_est.replace(hour=16, minute=15, second=0, microsecond=0)
    post_market_end = now_est.replace(hour=20, minute=0, second=0, microsecond=0)


    if market_start <= now_est <= market_end:
        return "Mid-day"
    elif now_est < market_start and now_est > pre_market_start:
        return "Pre-market"
    elif market_end < now_est <= post_market_end:
        return "Post-market"
    else:
        return "Market Closed"




# Function to fetch stock information
def fetch_stock_info(symbol):
    """Fetch stock information from an API."""
    api_url = f"https://api.cloudquote.io/fcon/getQuote.json?symbol={symbol}&T={GETQUOTE_API_KEY}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json().get('rows')[0]
    else:
        st.error('Failed to fetch stock information. Please check the symbol and try again.')
        return None


# Function to generate article
def generate_article(symbol, stock_info,time_period):
    """
        Generate a financial article based on stock information and time period.

        Parameters:
        - symbol: The stock symbol.
        - stock_info: A dictionary containing information about the stock.
        - time_period: The selected time period for the article context.

        Returns:
        A string containing the generated article.
    """

    try:
        article = ""
        change_percent = round(stock_info.get('ChangePercent', 0), 3)
        prompt = ""
        after_market_prompt =""
            # Construct the prompt from stock information
        if time_period == "Mid-day":
            open_price = round(stock_info.get("Open"), 3)
            open_present_prompt = " " if not open_price else f"opened today at ${open_price}"
            prompt = (f"Write an engaging informative article in 100 words about the stock XYZ {open_present_prompt} , "
                        f"currently trading at ${round(stock_info.get('Price', 0), 3)}, previous session close p"
                        f"rice was ${round(stock_info.get('PrevClose', 0), 3)}, current volume is "
                        f"{stock_info.get('Volume', 0)}")
            if change_percent > 0:
                prompt = prompt + f"and change percent from market open till now is {change_percent}"

        elif time_period == "Pre-market":
            
            change_percent = round((round(stock_info.get('AfterHoursPrice', 0), 3) / round(stock_info.get('PrevClose', 0),
                                                                                        3) - 1) * 100,3)
            trend = "bullish" if change_percent > 0 else "bearish"

            prompt = (f"Write an engaging informative article in 100 words about the stock XYZ that is trading in {trend} trend at in pre market session "
                        f"price ${round(stock_info.get('AfterHoursPrice', 0), 3)}, previous session close p"
                        f"rice was ${round(stock_info.get('PrevClose', 0), 3)}, current volume is "
                        f"{stock_info.get('Volume', 0)}")
            
            prompt = prompt + f"and change percent from market open till now is {change_percent}. "
            if change_percent > 20:
                prompt = prompt + f"Article should sound like exciting announcement "
            elif change_percent > 0:
                prompt = prompt + f"Article should sound like a announcement"


        elif time_period == "Post-market":
            # after market close
            open_price = round(stock_info.get("Open", 0), 3)
            open_present_prompt = " " if open_price == 0 else f"opened today at ${open_price}"

            change_percent = round(stock_info.get("ChangePercent", 0), 3)
            change_percent_prompt = ""


            if change_percent == 0 and open_price != 0:
                change_percent = (round(stock_info.get('Price', 0), 3 / open_price - 1)) * 100

            if change_percent > 0:
                change_percent_prompt = "showed bullish movement "
            elif change_percent < 0:
                change_percent_prompt = "showed bearish movement"
            else:
                after_market_price = round(stock_info.get("AfterHoursPrice", 0), 3)
                after_market_prompt = " " if not open_price == 0 else (f"after market session ended at  "
                                                                        f"${after_market_price}")

            prompt = (f"Write an informative article in 100 words about the stock XYZ {open_present_prompt} , "
                        f"{change_percent_prompt} , closed at price ${round(stock_info.get('Price', 'N/A'), 3)}, {after_market_prompt}, current volume is "
                        f"{stock_info.get('Volume', 0)}")

            if change_percent!=0:
                prompt = prompt + f"and change in percent from market open till now is {change_percent}. "
                if change_percent < -20:
                    prompt = prompt + f"Article should sound like announcement for major stock fall"
                elif change_percent > 20:
                    prompt = prompt + f"Article should sound like a massive price rise  "

        elif time_period =="Market Closed":
            return "No article generated"

        # st.text(f"PROMPT : {prompt}")

        company_name = stock_info.get('Name', 'N/A')
        # symbol = stock_info.get('Symbol', 'N/A')
        exchange = stock_info.get('ExchangeShortName', 'N/A').upper()

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a financial analyst"},
                    {"role": "user", "content": prompt}
                    ],

            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                article = article + chunk.choices[0].delta.content

        time.sleep(10)

        article = article.replace('XYZ', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('XYZ stock', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('xyz', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('stock XYZ', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('stock xyz', f' {company_name}({exchange}:{symbol}) ')

        article = article.replace('The stock of company, XYZ', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('The company, XYZ', f' {company_name}({exchange}:{symbol}) ')
        article = article.replace('The company, XYZ', f' {company_name}({exchange}:{symbol}) ')

        return article

    except Exception as e:
        st.error(f"An error occurred while generating the article: {e}")
        return None


# Main app logic
if symbol:
    # Fetch stock information
    stock_info = fetch_stock_info(symbol)
    if stock_info:
        # Display stock information
        st.write('Name:', stock_info.get('Name', 'N/A'))
        st.write('Price:', round(stock_info.get('Price', 'N/A'), 3))
        st.write('Previous Close:', round(stock_info.get('PrevClose', 'N/A'), 3))
        st.write('Volume:', stock_info.get('Volume', 'N/A'))
        st.write('Exchange Short Name:', stock_info.get('ExchangeShortName', 'N/A').upper())
        # st.write('Change Percent:', round(stock_info.get('ChangePercent', 'N/A'), 3))
        st.write('After Hours Price:', round(stock_info.get('AfterHoursPrice', 'N/A'), 3))
        after_hours_trade_time_unix =  round(stock_info.get('AfterHoursTradeTime', 'N/A'), 3)
        

                # Convert Unix timestamp to datetime in UTC
        after_hours_trade_time_utc = datetime.fromtimestamp(after_hours_trade_time_unix, tz=timezone.utc)
        
        # Convert UTC datetime to Eastern Standard Time (EST) timezone
        est_timezone = timezone(timedelta(hours=-5))  # EST is UTC-5
        after_hours_trade_time_est = after_hours_trade_time_utc.astimezone(est_timezone)
        st.write('AfterHoursTradeTime:',after_hours_trade_time_est)
        
        # Check if the converted date is today's date
        today_date_est = datetime.now(est_timezone).date()
        st.write('Current Time:',today_date_est)
        is_today = after_hours_trade_time_est.date() == today_date_est

        # Assign market_open based on the condition
        market_open = True if is_today else False

        # Button to generate article

        if stock_info.get('Open') or  stock_info.get('ChangePercent',0)!=0 or market_open:
            if st.button('Get Article'):
                time_period = get_time_period()
                st.write(f"Current time period in EST: {time_period}")

                article = generate_article(symbol, stock_info,time_period)
                #add header
                article = f"New York, {today_date_est} : ({stock_info.get('ExchangeShortName', 'N/A').upper()}:{symbol.upper()})\n" + article
                if article:
                    st.text_area("Generated Article", article, height=300)
                else:
                    st.error('Failed to generate an article.')
        else:
            st.error("Failed to generate an article. Market is closed.")
    else:
        st.error('Failed to fetch stock information. Please check the symbol and try again.')
