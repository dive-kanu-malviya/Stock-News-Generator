
# Stock Information Viewer

## Overview
The Stock Information Viewer is a Streamlit application designed to generate financial articles for all American stocks. It utilizes real-time stock price information, the time of the day, and the trend of the stock as input parameters. This tool aims to assist financial analysts by automating the creation of informative and engaging articles about stock movements.

## Features
- Fetch real-time stock price information.
- Generate articles based on the selected time of the day and stock trend (Mid-day, Pre-market-bullish, Pre-market-bearish, Post-market).
- Customizable for any American stock symbol.
- Uses OpenAI's GPT-3.5-turbo model for generating high-quality, informative articles.

## Installation

Before running this application, ensure you have Python and Streamlit installed on your system. You also need an API key from OpenAI and access to the stock information API.

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd <project-directory>
   ```
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Set your OpenAI API key as an environment variable for security reasons. You can do this by adding the following line to your `.bashrc` or `.bash_profile` file:
```
export OPENAI_API_KEY='your_openai_api_key_here'
```
Remember to replace `'your_openai_api_key_here'` with your actual OpenAI API key.

## Running the Application

After installing the required packages and setting up your API key, you can run the application using Streamlit:
```
streamlit run app.py
```

Replace `app.py` with the path to your script if it's named differently.

## Usage

1. **Enter Stock Symbol**: Start by entering the stock symbol for which you want to generate an article.
2. **Fetch Stock Information**: Click the 'Get Stock Information' button to fetch the latest stock data.
3. **Select Time and Trend**: Choose the relevant time of day and trend for your article using the dropdown menu.
4. **Generate Article**: Click the 'Get Article' button to generate your financial article based on the stock's current data.

## Contributing

Contributions to improve the Stock Information Viewer are welcome. Please feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
