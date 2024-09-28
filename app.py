import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Function to visualize stock prices, moving averages, volume, and RSI
def visualize_combined_chart(df, symbol):
    # Create a figure with two rows and a shared x-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        row_heights=[0.7, 0.3], vertical_spacing=0.05,
                        specs=[[{"secondary_y": True}], [{}]])  # Secondary y-axis for the first row (volume)

    # Add price and moving averages (1st quadrant)
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['Close'], name='Close Price', line=dict(color='blue')),
        row=1, col=1, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['MA20'], name='20-Day MA', line=dict(color='green')),
        row=1, col=1, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['MA50'], name='50-Day MA', line=dict(color='orange')),
        row=1, col=1, secondary_y=False
    )
    
    # Add volume as a bar chart (1st quadrant with secondary y-axis)
    fig.add_trace(
        go.Bar(x=df['Datetime'], y=df['Volume'], name='Volume', opacity=0.3, marker_color='purple'),
        row=1, col=1, secondary_y=True
    )

    # Add RSI (2nd quadrant)
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['RSI'], name='RSI', line=dict(color='blue')),
        row=2, col=1
    )

    # Update layout for the figure
    fig.update_layout(
        title=f'{symbol} Stock Price, Moving Averages, and Volume',
        xaxis_title='Date',
        showlegend=True,
        height=700,
    )
    
    # Update y-axes titles and ranges
    fig.update_yaxes(title_text="Price", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Volume", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])  # RSI y-axis range

    return fig

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
            
            st.subheader('3. Beta')
            st.markdown(info.get('beta', 'No information available'))
            
            st.subheader('4. Dividend')
            st.markdown(info.get('dividendRate', 'No information available'))
            
            # Get stock data
            df = get_stock_data(symbol, period='1y', interval='1d')
            
            # Visualize detailed chart
            st.subheader('5. Stock Chart')
            detailed_chart_fig = visualize_detailed_chart(df, symbol)
            st.plotly_chart(detailed_chart_fig)
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")

# Replaced Tab 3 with combined chart
with tab3:
    st.sidebar.header('Settings')
    symbol = st.sidebar.selectbox('Stock Symbol', top_50_stocks)

    if symbol:
        st.header(f'Analysis for {symbol}')
        
        # Get stock data
        df = get_stock_data(symbol, period='1d', interval='1m')
        
        # Calculate moving averages and technical indicators
        df = calculate_moving_averages(df)
        df = calculate_indicators(df)
        
        # Create combined chart with price, volume, and RSI
        combined_chart_fig = visualize_combined_chart(df, symbol)
        
        # Display the combined chart
        st.plotly_chart(combined_chart_fig)

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
