import streamlit as st
import requests
import os
import time

# Set the title of the app
st.title('Stock News Generator')

st.write("This application creates financial articles for all US stocks based on price information, time of the day and trend of the stock as input by the financial analyst")

# Input for stock symbol
symbol = st.text_input('Enter Stock Symbol').upper()
######
import requests
from openai import OpenAI
try:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    GETQUOTE_API_KEY=os.environ['GETQUOTE_API_KEY']
except KeyError as e:
    st.error(f"Environment variable {e} not set. Please check your .env file or environment configuration.")

client = OpenAI(api_key=OPENAI_API_KEY)


# API URL

# Check if the symbol has been entered to avoid unnecessary API calls
if symbol:
    # Your OpenAI API key - Ensure to use environment variables for security
    OPENAI_API_KEY =  os.environ['OPENAI_API_KEY']

    # Function to fetch stock information
    def fetch_stock_info(symbol):
        api_url = f"https://api.cloudquote.io/fcon/getQuote.json?symbol={symbol}&T={GETQUOTE_API_KEY}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json().get('rows')[0]
        else:
            return None

    # Function to generate article
    def generate_article(symbol, stock_info, time_period):

        article = ""
        change_percent = round(stock_info.get('ChangePercent', 0),3)
        try:
            # Construct the prompt from stock information
            if time_period =="Mid-day":
                open_price = round(stock_info.get("Open"),3)
                open_present_prompt = " " if not open_price else f"opened today at ${open_price}"
                prompt = f"Write an engaging informative article in 100 words about the stock XYZ {open_present_prompt} , currently trading at ${round(stock_info.get('Price', 0),3)}, previous session close price was ${round(stock_info.get('PrevClose', 0),3)}, current volume is {stock_info.get('Volume', 0)}"
                if change_percent > 0:
                    prompt = prompt + f"and change percent from market open till now is {change_percent}"

            elif time_period == "Pre-market-bullish":
                prompt = f"Write an engaging informative article in 100 words about the stock XYZ that opened at bullish price ${round(stock_info.get('AfterHoursPrice', 0),3)}, previous session close price was ${round(stock_info.get('PrevClose', 0),3)}, current volume is {stock_info.get('Volume', 0)}"
                change_percent = (round(stock_info.get('AfterHoursPrice', 0),3) / round(stock_info.get('PrevClose', 0),3)-1)*100
                
                if change_percent > 0:
                    prompt = prompt + f"and change percent from market open till now is {change_percent}. "
                if change_percent > 20:
                    prompt = prompt + f"Article should sound like exciting announcement "


            elif time_period == "Pre-market-bearish":
                prompt = f"Write an engaging informative article in 100 words about the stock XYZ that opened at bearish price ${round(stock_info.get('AfterHoursPrice', 0),3)}, previous session close price was ${round(stock_info.get('PrevClose', 0),3)}, current volume is {stock_info.get('Volume', 0)}"
                change_percent = (round(stock_info.get('AfterHoursPrice', 0),3) / round(stock_info.get('PrevClose',0),3)-1)*100

                if change_percent < 0:
                    prompt = prompt + f"and change percent from market open till now is {change_percent}. "
                if change_percent < -20:
                    prompt = prompt + f"Article should sound like announcement for major stock fall"
            
            elif time_period == "Post-market":
                #after market close
                open_price = round(stock_info.get("Open"),3)
                open_present_prompt = " " if not open_price else f"opened today at ${open_price}"

                change_percent = round(stock_info.get("ChangePercent",0),3)
                change_percent_prompt =""

                if change_percent==0:
                    change_percent = (round(stock_info.get('Price', 0),3/open_price-1))*100

                if change_percent > 0:
                    change_percent_prompt = "showed bullish movement " 
                elif change_percent < 0:
                    change_percent_prompt = "showed bearish movement"

                prompt = f"Write an informative article in 100 words about the stock XYZ {open_present_prompt} , {change_percent_prompt} , closed at price ${round(stock_info.get('Price', 'N/A'),3)}"
                

                
                prompt = prompt + f"and change in percent from market open till now is {change_percent}. "
                if change_percent < -10:
                    prompt = prompt + f"Article should sound like announcement for major stock fall"
                if change_percent > 20:
                    prompt = prompt + f"Article should sound like exciting announcement "

            # st.text(f"PROMPT : {prompt}")


        

            
            company_name = stock_info.get('Name', 'N/A')
            # symbol = stock_info.get('Symbol', 'N/A')
            exchange = stock_info.get('ExchangeShortName', 'N/A').upper()

            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[ {"role":"system", "content":"You are a financial analyst"},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": "Do not mention any trading symbol information"}],
                # messages=[{"role": "user", "content": "Say this is test"}],

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



            return article 
        
        except Exception as e:
            st.error(f"An error occurred while generating the article: {e}")
            return None
    

    # Use session state to store the stock info and prevent refetching on every interaction
    if 'stock_info' not in st.session_state or st.button('Get Stock Information'):
        st.session_state.stock_info = fetch_stock_info(symbol)

    if st.session_state.stock_info:
        stock_info = st.session_state.stock_info
        # Display stock information
        st.write('Name:', stock_info.get('Name', 'N/A'))
        st.write('Price:', round(stock_info.get('Price', 'N/A'), 3))
        st.write('PrevClose:', round(stock_info.get('PrevClose', 'N/A'), 3))
        st.write('Volume:', stock_info.get('Volume', 'N/A'))
        st.write('ExchangeShortName:', stock_info.get('ExchangeShortName', 'N/A').upper())
        st.write('ChangePercent:', round(stock_info.get('ChangePercent', 'N/A'), 3))

        # Radio buttons for time selection
        time_option = st.selectbox("Select Time and Trend", ('Mid-day', 'Pre-market-bullish', 'Pre-market-bearish', 'Post-market'))

        # Generate article button
        if st.button('Get Article'):
            article = generate_article(symbol, stock_info, time_option)
            if article:
                st.text_area("ChatGPT Article", article, height=300)
            else:
                st.error('Failed to generate an article.')
    else:
        st.error('Failed to fetch stock information. Please check the symbol and try again.')
