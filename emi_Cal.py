import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import requests

def fetch_real_time_rates():
    return {
        "Home Loan": 8.30,
        "Personal Loan": 12.00,
        "Car Loan": 9.00,
        "Education Loan": 8.50,
        "Business Loan": 10.50,
    }

def calculate_emi(principal, annual_rate, tenure_years):
    monthly_rate = annual_rate / 12 / 100
    tenure_months = tenure_years * 12
    emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
    return emi, tenure_months

def generate_amortization_schedule(principal, annual_rate, tenure_years, prepayment=0):
    monthly_rate = annual_rate / 12 / 100
    tenure_months = tenure_years * 12
    balance = principal
    schedule = []

    for month in range(1, tenure_months + 1):
        interest_payment = balance * monthly_rate
        emi, _ = calculate_emi(balance, annual_rate, tenure_years - (month - 1) / 12)
        principal_payment = emi - interest_payment
        balance -= (principal_payment + prepayment)
        if balance < 0:
            balance = 0
        schedule.append((month, emi, principal_payment, interest_payment, balance))
        if balance == 0:
            break

    df = pd.DataFrame(schedule, columns=['Month', 'EMI', 'Principal Payment', 'Interest Payment', 'Remaining Balance'])
    return df

def calculate_affordability(salary, expenses, saving_percent=30):
    disposable_income = salary - expenses
    max_emi = (saving_percent / 100) * disposable_income
    return max_emi

st.set_page_config(layout="wide")
st.markdown("<h1 style='font-size:22px;'>Advanced EMI Calculator for Indian Consumers - 2025</h1>", unsafe_allow_html=True)

# Fetch real-time interest rates
rates = fetch_real_time_rates()
tenures = {"Home Loan": 20, "Personal Loan": 5, "Car Loan": 7, "Education Loan": 10, "Business Loan": 15}

# Sidebar for Inputs
st.sidebar.markdown("<h3 style='font-size:16px;'>Loan Type Selection</h3>", unsafe_allow_html=True)
loan_type = st.sidebar.selectbox("Select Loan Type", list(rates.keys()))
default_rate = rates.get(loan_type, 8.0)
default_tenure = tenures.get(loan_type, 10)

st.sidebar.markdown("<h3 style='font-size:16px;'>Loan Details</h3>", unsafe_allow_html=True)
principal = st.sidebar.number_input("Principal Loan Amount (₹)", min_value=0.0, value=500000.0, step=10000.0)
annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.0, value=default_rate, step=0.1)
tenure_years = st.sidebar.number_input("Loan Tenure (Years)", min_value=0, value=default_tenure, step=1)
prepayment = st.sidebar.number_input("Monthly Prepayment Amount (₹)", min_value=0.0, value=0.0, step=1000.0)

# Loan Affordability Section
st.sidebar.markdown("<h3 style='font-size:16px;'>Loan Affordability Estimator</h3>", unsafe_allow_html=True)
salary = st.sidebar.number_input("Monthly Salary (₹)", min_value=0.0, value=50000.0, step=5000.0)
expenses = st.sidebar.number_input("Monthly Expenses (₹)", min_value=0.0, value=20000.0, step=5000.0)
max_emi = calculate_affordability(salary, expenses)
st.sidebar.markdown(f"<h4 style='font-size:14px;'>Max Affordable EMI: ₹{max_emi:,.2f}</h4>", unsafe_allow_html=True)

emi = None
if st.sidebar.button("Calculate EMI"):
    emi, tenure_months = calculate_emi(principal, annual_rate, tenure_years)
    st.sidebar.markdown(f"<h4 style='font-size:14px;'>Your Monthly EMI: ₹{emi:,.2f}</h4>", unsafe_allow_html=True)

# Loan Comparison Mode
st.markdown("<h2 style='font-size:18px;'>Compare Loan Options</h2>", unsafe_allow_html=True)
st.markdown("Select different loan types to compare their EMI calculations.")
comparison_loans = st.multiselect("Select Loan Types to Compare", list(rates.keys()))
comparison_data = []
for loan in comparison_loans:
    emi, _ = calculate_emi(principal, rates[loan], tenures[loan])
    comparison_data.append((loan, emi))
comparison_df = pd.DataFrame(comparison_data, columns=["Loan Type", "EMI (₹)"])
st.dataframe(comparison_df, width=300)

# Main Content Layout
st.markdown("<h2 style='font-size:18px;'>Loan Summary</h2>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:16px;'>EMI: ₹{emi:,.2f}</h3>" if emi else "<h3 style='font-size:16px;'>EMI: -</h3>", unsafe_allow_html=True)

st.markdown("<h3 style='font-size:16px;'>Loan Balance Over Time</h3>", unsafe_allow_html=True)
if emi:
    schedule = generate_amortization_schedule(principal, annual_rate, tenure_years, prepayment)
    fig = px.line(schedule, x='Month', y='Remaining Balance', title='Loan Amortization Schedule',
                labels={'Month': 'Month', 'Remaining Balance': 'Remaining Loan Balance (₹)'},
                markers=True)
    st.plotly_chart(fig)

st.markdown("<h3 style='font-size:16px;'>Payment Breakdown</h3>", unsafe_allow_html=True)
if emi:
    fig_pie = px.pie(values=[schedule['Principal Payment'].sum(), schedule['Interest Payment'].sum()], 
                    names=['Principal', 'Interest'], 
                    title='Total Payment Breakdown')
    st.plotly_chart(fig_pie)

st.markdown("<h3 style='font-size:16px;'>Amortization Schedule</h3>", unsafe_allow_html=True)
if emi:
    st.dataframe(schedule)

st.markdown("<h3 style='font-size:16px;'>Download Report</h3>", unsafe_allow_html=True)
if emi:
    st.markdown(create_download_link(schedule), unsafe_allow_html=True)
