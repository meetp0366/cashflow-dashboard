import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Cash Flow Dashboard", layout="wide")

# Custom CSS


st.markdown("""
<style>
.kpi-card {
    background-color: #1f2c3c;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}
.kpi-title {
    font-size: 18px;
    color: #cbd5e1;
}
.kpi-value {
    font-size: 30px;
    font-weight: bold;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)


# Categories


INCOME_CATEGORIES = ["Sales", "Service Revenue"]

EXPENSE_CATEGORIES = [
    "Rent",
    "Electricity",
    "Insurance",
    "Raw Materials",
    "Shipping Cost",
    "Maintenance",
    "Transportation",
    "Salaries"
]


# Data

if "transactions" not in st.session_state:

    st.session_state.transactions = pd.DataFrame({
        "Date": [
            date(2025,1,2), date(2025,1,3),
            date(2025,1,5), date(2025,1,7),
            date(2025,1,9), date(2025,1,11),
            date(2025,1,13), date(2025,1,15),
            date(2025,1,17), date(2025,1,19),
            date(2025,1,21), date(2025,1,23),
            date(2025,1,25), date(2025,1,27),
            date(2025,1,29),

            date(2025,2,1), date(2025,2,3),
            date(2025,2,5), date(2025,2,7),
            date(2025,2,9), date(2025,2,11),
            date(2025,2,13), date(2025,2,15),
            date(2025,2,17), date(2025,2,19),
            date(2025,2,21), date(2025,2,23),
            date(2025,2,25), date(2025,2,27),
            date(2025,2,28),
        ],
        "Type": [
            "Income","Expense","Income","Expense","Income","Expense",
            "Income","Expense","Income","Expense","Income","Expense",
            "Income","Expense","Income",

            "Income","Expense","Income","Expense","Income","Expense",
            "Income","Expense","Income","Expense","Income","Expense",
            "Income","Expense","Income"
        ],
        "Category": [
            "Sales","Rent","Sales","Electricity","Service Revenue","Raw Materials",
            "Sales","Salaries","Sales","Shipping Cost","Service Revenue","Maintenance",
            "Sales","Transportation","Service Revenue",

            "Sales","Rent","Service Revenue","Insurance","Sales","Raw Materials",
            "Sales","Salaries","Sales","Transportation","Service Revenue","Electricity",
            "Sales","Shipping Cost","Service Revenue"
        ],
        "Amount": [
            60000,40000,55000,10000,50000,15000,
            62000,30000,45000,8000,40000,6000,
            58000,9000,42000,

            45000,50000,35000,20000,40000,30000,
            38000,45000,42000,15000,30000,10000,
            32000,12000,25000
        ]
    })

# Sidebar

st.sidebar.title("💸 Add Transaction")

date_input = st.sidebar.date_input("Date", value=date.today())
type_option = st.sidebar.selectbox("Type", ["Income", "Expense"])

category = st.sidebar.selectbox(
    "Category",
    INCOME_CATEGORIES if type_option == "Income" else EXPENSE_CATEGORIES
)

amount = st.sidebar.number_input("Amount", min_value=0)

if st.sidebar.button("Add Transaction"):
    new_row = pd.DataFrame(
        [[date_input, type_option, category, amount]],
        columns=["Date", "Type", "Category", "Amount"]
    )
    st.session_state.transactions = pd.concat(
        [st.session_state.transactions, new_row],
        ignore_index=True
    )
    st.success("Transaction Added Successfully!")
    st.rerun()

# Date Filter


df = st.session_state.transactions.copy()
df["Date"] = pd.to_datetime(df["Date"])

min_date = df["Date"].min()
max_date = df["Date"].max()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

filtered_df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
].copy()

# Remove time display
filtered_df["Date"] = filtered_df["Date"].dt.date

# KPI Calculations


total_income = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
total_expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
net_cash = total_income - total_expense
profit_margin = (net_cash / total_income * 100) if total_income != 0 else 0
profit_color = "#22c55e" if net_cash >= 0 else "#ef4444"

# Dashboard


st.title("📊 Small Business Cash Flow Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Income</div>
        <div class="kpi-value">₹ {total_income:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Expense</div>
        <div class="kpi-value">₹ {total_expense:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Net Profit</div>
        <div class="kpi-value" style="color:{profit_color}">
            ₹ {net_cash:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Profit Margin</div>
        <div class="kpi-value">{profit_margin:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Charts Section 

col1, col2 = st.columns([2, 1])  

# Daily Stock Style Graph

with col1:
    if not filtered_df.empty:

        temp_df = filtered_df.copy()

        temp_df["Signed Amount"] = temp_df.apply(
            lambda row: row["Amount"] if row["Type"] == "Income" else -row["Amount"],
            axis=1
        )

        temp_df = temp_df.sort_values("Date")
        temp_df["Cumulative Cash"] = temp_df["Signed Amount"].cumsum()

        fig = px.line(temp_df, x="Date", y="Cumulative Cash")

        fig.update_layout(
            template="plotly_dark",
            height=450,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Cash Balance"
        )

        fig.add_hline(y=0, line_dash="dash", line_color="white")

        st.plotly_chart(fig, use_container_width=True)


# Expense Pie

with col2:
    expense_data = filtered_df[filtered_df["Type"] == "Expense"]

    if not expense_data.empty:
        fig_pie = px.pie(expense_data, names="Category", values="Amount")
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

# Table


st.subheader("📋 Transaction History")
st.dataframe(filtered_df, use_container_width=True)

# Export CSV


csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Transactions",
    data=csv,
    file_name="cashflow_transactions.csv",
    mime="text/csv",
)

# Delete Transaction


st.subheader("🗑 Delete Transaction")

delete_index = st.number_input(
    "Enter Row Index to Delete",
    min_value=0,
    max_value=len(df)-1,
    step=1
)

if st.button("Delete Selected Transaction"):
    st.session_state.transactions = df.drop(delete_index).reset_index(drop=True)
    st.success("Transaction Deleted Successfully!")
    st.rerun()
