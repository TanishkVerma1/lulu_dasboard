import streamlit as st
import pandas as pd
import numpy as np

# ----- Step 1: Generate synthetic data -----
np.random.seed(42)

n_rows = 100
data = {
    "Customer_ID": [f"CUST{i+1}" for i in range(n_rows)],
    "Age_Group": np.random.choice(["18-25", "26-40", "41-60", "60+"], n_rows),
    "Gender": np.random.choice(["Male", "Female"], n_rows),
    "Location": np.random.choice(["Dubai", "Abu Dhabi", "Sharjah", "Ajman"], n_rows),
    "Category": np.random.choice(["Groceries", "Electronics", "Clothing", "Household"], n_rows),
    "Sales_Amount": np.random.randint(20, 1000, n_rows)
}

df = pd.DataFrame(data)

# ----- Step 2: Streamlit Dashboard -----
st.title("🛒 Lulu Hypermarket Sales Dashboard - UAE")

st.sidebar.header("Filter Sales Data")
age_filter = st.sidebar.multiselect("Select Age Group", df["Age_Group"].unique())
gender_filter = st.sidebar.multiselect("Select Gender", df["Gender"].unique())
location_filter = st.sidebar.multiselect("Select Location", df["Location"].unique())
category_filter = st.sidebar.multiselect("Select Category", df["Category"].unique())

# Apply filters
filtered_df = df.copy()
if age_filter:
    filtered_df = filtered_df[filtered_df["Age_Group"].isin(age_filter)]
if gender_filter:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
if location_filter:
    filtered_df = filtered_df[filtered_df["Location"].isin(location_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]

st.subheader("Filtered Sales Data")
st.dataframe(filtered_df)

# Charts
st.subheader("Sales by Category")
st.bar_chart(filtered_df.groupby("Category")["Sales_Amount"].sum())

st.subheader("Sales by Location")
st.bar_chart(filtered_df.groupby("Location")["Sales_Amount"].sum())

st.subheader("Sales by Gender")
st.bar_chart(filtered_df.groupby("Gender")["Sales_Amount"].sum())

st.subheader("Sales by Age Group")
st.bar_chart(filtered_df.groupby("Age_Group")["Sales_Amount"].sum())
