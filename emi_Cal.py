import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

st.title("Advanced EMI Calculator for Indian Consumers - 2025")

loan_type = st.selectbox("Select Loan Type", ["Home Loan", "Personal Loan", "Car Loan"])

if loan_type == "Home Loan":
    default_rate = 7.0
    default_tenure = 20
elif loan_type == "Personal Loan":
    default_rate = 12.0
    default_tenure = 5
else:
    default_rate = 9.0
    default_tenure = 7

principal = st.number_input("Principal Loan Amount (₹)", min_value=0.0, value=500000.0, step=10000.0)
annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=default_rate, step=0.1)
tenure_years = st.number_input("Loan Tenure (Years)", min_value=0, value=default_tenure, step=1)
prepayment = st.number_input("Monthly Prepayment Amount (₹)", min_value=0.0, value=0.0, step=1000.0)

if st.button("Calculate EMI"):
    emi, tenure_months = calculate_emi(principal, annual_rate, tenure_years)
    st.write(f"Your monthly EMI is: ₹{emi:,.2f}")

    schedule = generate_amortization_schedule(principal, annual_rate, tenure_years, prepayment)
    st.write("Amortization Schedule:")
    st.dataframe(schedule)

    # Plotting the remaining balance over time
    fig, ax = plt.subplots()
    ax.plot(schedule['Month'], schedule['Remaining Balance'], label='Remaining Balance')
    ax.set_xlabel('Month')
    ax.set_ylabel('Remaining Loan Balance (₹)')
    ax.set_title('Loan Amortization Schedule')
    ax.legend()
    st.pyplot(fig)
