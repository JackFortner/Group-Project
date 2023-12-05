import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os 
from sqlalchemy import create_engine

# Database setup (SQLite in this example)
engine = create_engine('sqlite:///roboadvisor.db')

def create_user_profile():
    st.title('User Profile Creation')
    name = st.text_input("Name")
    financial_goal = st.number_input("Financial Goal", min_value=1000)
    risk_tolerance = st.slider("Risk Tolerance", 1, 10, 5)
    investment_horizon = st.selectbox("Investment Horizon", ["Short-term", "Medium-term", "Long-term"])
    if st.button('Create Profile'):
        user_profile = pd.DataFrame({
            "name": [name],
            "financial_goal": [financial_goal],
            "risk_tolerance": [risk_tolerance],
            "investment_horizon": [investment_horizon]
        })
        user_profile.to_sql('profiles', con=engine, if_exists='append', index=False)
        st.success('Profile Created')

def recommend_portfolio():
    st.title("Portfolio Recommendation")
    profiles = pd.read_sql('profiles', con=engine)

    if not profiles.empty:
        for _, row in profiles.iterrows():
            user_risk_tolerance = row['risk_tolerance']
            recommended_portfolio = get_recommended_portfolio(user_risk_tolerance)
            investment_allocation = get_investment_allocation(recommended_portfolio, row['financial_goal'], row['investment_horizon'])
            st.write(f"{row['name']}'s Recommended Portfolio: {recommended_portfolio['name']}")
            st.write("Investment Allocation:")
            st.table(investment_allocation)
    else:
        st.write("No profiles available. Please add user profiles.")

def get_recommended_portfolio(risk_tolerance, investment_horizon):
 

    if investment_horizon == "Short-term":
        # Prefer conservative portfolios for short-term horizons
        if risk_tolerance <= 7:
            return 'Conservative'
        else:
            return 'Moderate'
    elif investment_horizon == "Medium-term":
        # Balanced approach for medium-term
        if risk_tolerance <= 4:
            return 'Conservative'
        elif risk_tolerance <= 7:
            return 'Moderate'
        else:
            return 'Aggressive'
    else:  # Long-term
        # Prefer more aggressive portfolios for long-term horizons
        if risk_tolerance <= 4:
            return 'Moderate'
        else:
            return 'Aggressive'

portfolios = {
        'Conservative': {'name': 'Conservative', 'risk': 2, 'return': 4},
        'Moderate': {'name': 'Moderate', 'risk': 5, 'return': 7},
        'Aggressive': {'name': 'Aggressive', 'risk': 8, 'return': 10}
    }

def recommend_portfolio():
    st.title("Portfolio Recommendation")
    profiles = pd.read_sql('profiles', con=engine)

    if not profiles.empty:
        for _, row in profiles.iterrows():
            user_risk_tolerance = row['risk_tolerance']
            investment_horizon = row['investment_horizon']
            recommended_portfolio_name = get_recommended_portfolio(user_risk_tolerance, investment_horizon)
            recommended_portfolio = portfolios[recommended_portfolio_name]
            investment_allocation = get_investment_allocation(recommended_portfolio, row['financial_goal'], row['investment_horizon'])
            st.write(f"{row['name']}'s Recommended Portfolio: {recommended_portfolio['name']}")
            st.write("Investment Allocation:")
            st.table(investment_allocation)
    else:
        st.write("No profiles available. Please add user profiles.")


def get_investment_allocation(portfolio, financial_goal, horizon):
    base_allocation = {
        'Conservative': {'Bonds': 70, 'ETFs': 20, 'Stocks': 10},
        'Moderate': {'Bonds': 40, 'ETFs': 30, 'Stocks': 30},
        'Aggressive': {'Bonds': 10, 'ETFs': 20, 'Stocks': 70}
    }

    # Adjust allocations based on financial goal
    if financial_goal < 5000:  # Lower goal, more conservative
        allocation_adjustment = {'Bonds': 10, 'ETFs': -5, 'Stocks': -5}
    elif 5000 <= financial_goal < 20000:  # Moderate goal
        allocation_adjustment = {'Bonds': 5, 'ETFs': 0, 'Stocks': -5}
    else:  # Higher goal, more aggressive
        allocation_adjustment = {'Bonds': -10, 'ETFs': 5, 'Stocks': 5}

    final_allocation = {
        asset: base_allocation[portfolio['name']][asset] + allocation_adjustment.get(asset, 0)
        for asset in base_allocation[portfolio['name']]
    }

    return pd.DataFrame(final_allocation, index=['% Allocation'])

def show_investment_options():
    st.title("Popular Investment Options")

    st.subheader("Stocks")
    st.write("1. Apple Inc. (AAPL)")
    st.write("2. Microsoft Corp. (MSFT)")
    st.write("3. Amazon.com Inc. (AMZN)")

    st.subheader("ETFs (Exchange Traded Funds)")
    st.write("1. SPDR S&P 500 ETF Trust (SPY)")
    st.write("2. iShares Russell 2000 ETF (IWM)")
    st.write("3. Vanguard Total Stock Market ETF (VTI)")

    st.subheader("Bonds")
    st.write("1. U.S. Treasury Bonds")
    st.write("2. Corporate Bonds (e.g., IBM Corp Bonds)")
    st.write("3. Municipal Bonds")

    st.write("Note: These are examples of popular investment options")



def track_performance(ticker):
    st.title("Performance Tracking")
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    plt.figure(figsize=(10, 5))
    plt.plot(hist['Close'])
    plt.title("Stock Closing Price Over Time")
    st.pyplot(plt)

def reset_entire_database():
    if os.path.exists("roboadvisor.db"):
        os.remove("roboadvisor.db")
        st.success("Entire database has been reset")
    else:
        st.error("Database file not found.")

def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose a function", ["Create Profile", "Portfolio Recommendation","Investment Options", "Performance Tracking", "Reset Database"])

    if choice == "Create Profile":
        create_user_profile()

    elif choice == "Portfolio Recommendation":
        recommend_portfolio()

    elif choice == "Investment Options":
        show_investment_options()

    elif choice == "Performance Tracking":
        ticker = st.sidebar.text_input("Enter a Stock Ticker", "AAPL")
        track_performance(ticker)

    elif choice == "Reset Database":
        st.warning("Warning: This will delete data permanently.")
        if st.button("Reset Entire Database"):
            reset_entire_database()

if __name__ == "__main__":
    main()
