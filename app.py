import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import ta
from io import BytesIO

# Static list of top 50 popular stocks (for demonstration)
top_50_stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'INTC', 'AMD',
    'V', 'JPM', 'JNJ', 'WMT', 'PG', 'DIS', 'MA', 'HD', 'PYPL', 'BAC',
    'VZ', 'ADBE', 'CMCSA', 'XOM', 'CSCO', 'PFE', 'T', 'PEP', 'KO', 'NKE',
    'MRK', 'ABT', 'ORCL', 'CRM', 'MCD', 'LLY', 'INTU', 'UNH', 'AVGO', 'CVX',
    'COST', 'ACN', 'NEE', 'DHR', 'WFC', 'TXN', 'TMO', 'UPS', 'MS', 'AMAT'
]

# Function to get historical stock data
def get_stock_data(symbol, period='1y', interval='1d'):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval=interval)
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'Datetime'}, inplace=True)
    df['Datetime'] = df['Datetime'].dt.tz_localize(None)
    return df

# Function to calculate moving averages
def calculate_moving_averages(df):
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    return df

# Function to calculate technical indicators
def calculate_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['MACD'] = ta.trend.MACD(df['Close']).macd()
    return df

# Function to visualize stock prices and moving averages
def visualize_prices(df, symbol):
    fig = px.line(df, x='Datetime', y=['Close', 'MA20', 'MA50'], title=f'{symbol} Stock Price and Moving Averages')
    fig.update_layout(yaxis_title='Price', xaxis_title='Date')
    return fig

# Function to visualize volume
def visualize_volume(df, symbol):
    fig = px.bar(df, x='Datetime', y='Volume', title=f'{symbol} Trading Volume')
    fig.update_layout(yaxis_title='Volume', xaxis_title='Date')
    return fig

# Function to visualize RSI
def visualize_rsi(df, symbol):
    fig = px.line(df, x='Datetime', y='RSI', title=f'{symbol} RSI (Relative Strength Index)')
    fig.update_layout(yaxis_title='RSI', xaxis_title='Date')
    return fig

# Function to visualize MACD
def visualize_macd(df, symbol):
    fig = px.line(df, x='Datetime', y='MACD', title=f'{symbol} MACD (Moving Average Convergence Divergence)')
    fig.update_layout(yaxis_title='MACD', xaxis_title='Date')
    return fig

# Function to get stock info
def get_stock_info(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

# Function to visualize detailed stock chart
def visualize_detailed_chart(df, symbol):
    fig = px.line(df, x='Datetime', y='Close', title=f'{symbol} Detailed Stock Chart')
    fig.update_layout(yaxis_title='Price', xaxis_title='Date')
    return fig

# Function to generate detailed report
def generate_detailed_report(symbol):
    stock = yf.Ticker(symbol)
    report = {
        "Stock Info": stock.info,
        "History (1 Month)": stock.history(period="1mo").reset_index(),
        "History Metadata": stock.history_metadata,
        ## "Actions": stock.actions, 
        ## "Capital Gains": stock.capital_gains, # only for mutual funds & etfs
        "Shares": stock.get_shares_full(start="2022-01-01", end=None).reset_index(),
        "Income Statement": stock.financials.reset_index(),
        "Quarterly Income Statement": stock.quarterly_financials.reset_index(),
        "Balance Sheet": stock.balance_sheet.reset_index(),
        "Quarterly Balance Sheet": stock.quarterly_balance_sheet.reset_index(),
        "Cash Flow": stock.cashflow.reset_index(),
        "Quarterly Cash Flow": stock.quarterly_cashflow.reset_index(),
        "Major Holders": stock.major_holders,
        "Institutional Holders": stock.institutional_holders,
        "Mutual Fund Holders": stock.mutualfund_holders,
        "Insider Transactions": stock.insider_transactions,
        "Insider Purchases": stock.insider_purchases,
        "Insider Roster Holders": stock.insider_roster_holders,
        "Recommendations": stock.recommendations.reset_index(),
        "Recommendations Summary": stock.recommendations_summary,
        "Upgrades Downgrades": stock.upgrades_downgrades.reset_index()
    }

    # Ensure all datetime columns are timezone unaware
    for key, value in report.items():
        if isinstance(value, pd.DataFrame):
            for col in value.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                value[col] = value[col].dt.tz_localize(None)

    return report

# Function to create a downloadable report
def create_downloadable_report(report, symbol):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    for key, value in report.items():
        if isinstance(value, pd.DataFrame):
            value.to_excel(writer, sheet_name=key[:31])
        else:
            pd.DataFrame([value]).to_excel(writer, sheet_name=key[:31])

    writer.close()
    output.seek(0)
    return output

# Streamlit app
st.title('Stock Analysis App')

# Tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["About this app", "In-Depth Stock Analysis", "Stock Analytics", "Reports"])

with tab1:
    st.header('About this app')
    st.markdown("""
    ## Stock Analysis App
    This app provides comprehensive stock analysis using historical price data, moving averages, and various technical indicators. 
    It also allows users to generate detailed financial reports for selected stocks from a predefined list of popular stocks.

    ### Target Users
    This app is particularly useful for:
    - **Individual Investors**: Who want to analyze stock performance and make informed investment decisions.
    - **Financial Analysts**: Who need detailed reports and technical indicators for professional analysis.
    - **Students and Educators**: Who are learning about financial markets and technical analysis.

    ## Instruction Manual

    ### Getting Started
    1. **Launching the App**: Run the script in a Streamlit environment. The command typically used is `streamlit run script_name.py`.
    2. **Navigating the Interface**: The app interface is divided into four main tabs accessible at the top of the app:
        - **Stock Analysis**: General stock analysis with various metrics.
        - **In-Depth Stock Analysis**: Detailed stock information and historical performance.
        - **Reports**: Generate and download comprehensive financial reports.
        - **About this app**: Information about the app.

    ### Using the "Stock Analysis" Tab
    1. **Select Stock Symbol**: Choose a stock symbol from the dropdown list on the sidebar.
    2. **Select Analysis Metrics**: Choose the metrics you want to analyze from the options provided:
        - Prices and Moving Averages
        - Trading Volume
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
    3. **View Analysis**: The selected metrics will be displayed as interactive Plotly charts. Detailed explanations for each metric will be shown below the charts.

    ### Using the "In-Depth Stock Analysis" Tab
    1. **Select Stock Symbol for In-Depth Analysis**: Choose a stock symbol from the dropdown list on the sidebar.
    2. **View In-Depth Analysis**: The app will display detailed information about the stock, including:
        - Business summary
        - Price-to-Earnings (P/E) ratio
        - Beta (volatility)
        - Dividend rate
    3. **Detailed Stock Chart**: A detailed stock chart for the past year will also be displayed.

    ### Using the "Reports" Tab
    1. **Select Stock Symbol for Detailed Reports**: Choose a stock symbol from the dropdown list on the sidebar.
    2. **Generate and View Report**: The app will generate a detailed financial report for the selected stock. Various sections of the report will be displayed, including stock history, financial statements, holders, and insider transactions.
    3. **Download Report**: A button will be provided to download the report as an Excel file.
    """)

with tab2:
    st.sidebar.header('In-Depth Stock Analysis Settings')
    symbol = st.sidebar.selectbox('Stock Symbol for In-Depth Analysis', top_50_stocks)
    
    if symbol:
        st.header(f'In-Depth Analysis for {symbol}')
        
        try:
            # Get stock info
            info = get_stock_info(symbol)
            
            # Display stock information
            st.subheader(f'1. What the {symbol} Stock Does')
            st.markdown(info.get('longBusinessSummary', 'No information available'))
            
            st.subheader('2. Price-to-Earnings (P/E) Ratio')
            st.markdown(info.get('trailingPE', 'No information available'))
            st.markdown("\nThe P/E ratio is a valuation ratio of a company's current share price compared to its per-share earnings. A high P/E ratio could mean that the stock is overvalued, or else that investors are expecting high growth rates in the future.")
            
            st.subheader('3. Beta')
            st.markdown(info.get('beta', 'No information available'))
            st.markdown("\nBeta is a measure of a stock's volatility in relation to the overall market. A beta greater than 1 indicates that the stock is more volatile than the market, while a beta less than 1 indicates that the stock is less volatile.")
            
            st.subheader('4. Dividend')
            st.markdown(info.get('dividendRate', 'No information available'))
            st.markdown("\nThe dividend is the distribution of a portion of a company's earnings, decided and managed by the company's board of directors, to a class of its shareholders. Dividends can be issued as cash payments, as shares of stock, or other property.")
            
            # Get stock data
            df = get_stock_data(symbol, period='1y', interval='1d')
            
            # Visualize detailed chart
            st.subheader('5. Stock Chart')
            detailed_chart_fig = visualize_detailed_chart(df, symbol)
            st.plotly_chart(detailed_chart_fig)
            st.markdown("### This chart shows the detailed stock price movements over a period of one year. It helps in analyzing the historical performance of the stock.")
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")

with tab3:
    st.sidebar.header('Settings')
    symbol = st.sidebar.selectbox('Stock Symbol', top_50_stocks)
    metrics = st.sidebar.multiselect(
        'Select Analysis Metrics',
        ['Prices and Moving Averages', 'Trading Volume', 'RSI (Relative Strength Index)', 'MACD (Moving Average Convergence Divergence)'],
        ['Prices and Moving Averages', 'Trading Volume', 'RSI (Relative Strength Index)', 'MACD (Moving Average Convergence Divergence)']
    )

    if symbol:
        st.header(f'Analysis for {symbol}')
        
        # Create placeholders for charts
        prices_placeholder = st.empty()
        st.markdown("### Prices and Moving Averages\nThis chart shows the closing price of the stock along with 20-day and 50-day moving averages. The moving averages help smooth out price data to better identify the direction of the trend over a longer period. The 20-day moving average reacts quicker to price changes than the 50-day moving average.")
        volume_placeholder = st.empty()
        st.markdown("### Trading Volume\nThis chart represents the number of shares traded during each time interval. High trading volumes can indicate high interest in the stock, potentially preceding significant price movements.")
        rsi_placeholder = st.empty()
        st.markdown("### RSI (Relative Strength Index)\nThe RSI is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100. Traditionally, an RSI above 70 is considered overbought, and below 30 is considered oversold.")
        macd_placeholder = st.empty()
        st.markdown("### MACD (Moving Average Convergence Divergence)\nThe MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a stock’s price. It consists of the MACD line (difference between the 12-day and 26-day EMA) and the signal line (9-day EMA of the MACD line). When the MACD line crosses above the signal line, it is a bullish signal, and when it crosses below, it is a bearish signal.")
        
        # Get stock data
        df = get_stock_data(symbol, period='1d', interval='1m')
        
        # Calculate moving averages and technical indicators
        df = calculate_moving_averages(df)
        df = calculate_indicators(df)
        
        # Update visualizations
        if 'Prices and Moving Averages' in metrics:
            prices_fig = visualize_prices(df, symbol)
            prices_placeholder.plotly_chart(prices_fig)
        if 'Trading Volume' in metrics:
            volume_fig = visualize_volume(df, symbol)
            volume_placeholder.plotly_chart(volume_fig)
        if 'RSI (Relative Strength Index)' in metrics:
            rsi_fig = visualize_rsi(df, symbol)
            rsi_placeholder.plotly_chart(rsi_fig)
            st.markdown("### RSI (Relative Strength Index)\nThe RSI is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100. Traditionally, an RSI above 70 is considered overbought, and below 30 is considered oversold.")
        if 'MACD (Moving Average Convergence Divergence)' in metrics:
            macd_fig = visualize_macd(df, symbol)
            macd_placeholder.plotly_chart(macd_fig)

with tab4:
    st.sidebar.header('Detailed Reports Settings')
    symbol = st.sidebar.selectbox('Stock Symbol for Detailed Reports', top_50_stocks)
    
    if symbol:
        st.header(f'Detailed Reports for {symbol}')
        
        try:
            # Generate detailed report
            report = generate_detailed_report(symbol)
            
            # Display detailed report sections
            for section, data in report.items():
                st.subheader(section)
                if isinstance(data, pd.DataFrame):
                    st.dataframe(data)
                else:
                    st.json(data)
            
            # Create downloadable report
            downloadable_report = create_downloadable_report(report, symbol)
            st.download_button(label="Download Report", data=downloadable_report, file_name=f'{symbol}_report.xlsx')
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            
