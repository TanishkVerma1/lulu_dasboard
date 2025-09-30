\
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Lulu Global Sales Dashboard", page_icon="🛍️", layout="wide")

# ==========================
# Synthetic GLOBAL dataset
# ==========================
@st.cache_data
def make_data(n_rows=100, seed=42):
    rng = np.random.default_rng(seed)
    # date span last 12 months
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.DateOffset(months=12)

    countries = ["UAE", "India", "Saudi Arabia", "Qatar", "Oman", "Bahrain"]
    cities_by_country = {
        "UAE": ["Dubai","Abu Dhabi","Sharjah","Ajman"],
        "India": ["Mumbai","Delhi","Bengaluru","Chennai"],
        "Saudi Arabia": ["Riyadh","Jeddah","Dammam"],
        "Qatar": ["Doha","Al Rayyan"],
        "Oman": ["Muscat","Salalah"],
        "Bahrain": ["Manama","Riffa"],
    }
    channels = ["Hypermarket","Market","Online"]
    genders = ["Male","Female"]
    age_groups = ["18-25","26-40","41-60","60+"]
    income_band = ["Low","Lower-Middle","Upper-Middle","High"]
    loyalty = ["None","Silver","Gold","Platinum"]
    pay_methods = ["Card","Cash","Wallet","BNPL"]
    categories = ["Groceries","Electronics","Clothing","Household","Beauty"]
    subcats = {
        "Groceries": ["Fresh Produce","Bakery","Dairy","Snacks"],
        "Electronics": ["Mobiles","Accessories","Appliances","TV"],
        "Clothing": ["Menswear","Womenswear","Kids"],
        "Household": ["Cleaning","Kitchen","Decor"],
        "Beauty": ["Skincare","Haircare","Fragrance"],
    }
    brands = {
        "Mobiles": ["Apple","Samsung","Xiaomi","OnePlus"],
        "Accessories": ["Boat","JBL","Anker","Sony"],
        "Appliances": ["Philips","Panasonic","LG","Toshiba"],
        "TV": ["LG","Samsung","Sony","TCL"],
        "Menswear": ["Levi's","H&M","Zara","Nike"],
        "Womenswear": ["H&M","Zara","Forever21","Mango"],
        "Kids": ["H&M","Zara","Mothercare","Nike"],
        "Fresh Produce": ["Local","Organic Farms"],
        "Bakery": ["In-house","Local"],
        "Dairy": ["Almarai","Lacnor","Nandini"],
        "Snacks": ["Lays","Pringles","Kurkure"],
        "Cleaning": ["Dettol","Harpic","Vim"],
        "Kitchen": ["Prestige","Tefal","Cello"],
        "Decor": ["HomeCentre","Ikea"],
        "Skincare": ["Nivea","L'Oreal","Neutrogena"],
        "Haircare": ["Dove","Head&Shoulders","Tresemme"],
        "Fragrance": ["Nike","Guess","Jaguar"]
    }

    rows = []
    order_ids = [f"ORD{1000+i}" for i in range(n_rows)]
    # Pre-build a pandas date_range, then sample per row and NORMALIZE to midnight Timestamp (no .date())
    dates = pd.date_range(start=start_date, end=today, freq="D")
    for oid in order_ids:
        country = rng.choice(countries)
        city = rng.choice(cities_by_country[country])
        channel = rng.choice(channels, p=[0.6,0.2,0.2])
        gender = rng.choice(genders)
        age_group = rng.choice(age_groups, p=[0.25,0.35,0.3,0.1])
        income = rng.choice(income_band, p=[0.2,0.35,0.3,0.15])
        tier = rng.choice(loyalty, p=[0.45,0.3,0.2,0.05])
        pay = rng.choice(pay_methods, p=[0.6,0.25,0.1,0.05])
        cat = rng.choice(categories, p=[0.4,0.2,0.18,0.15,0.07])
        sub = rng.choice(subcats[cat])
        brand_list = brands.get(sub, ["Store Brand"])
        brand = rng.choice(brand_list)
        units = int(max(1, rng.poisson(2 if cat!="Electronics" else 1)))
        base_price = {
            "Groceries": rng.uniform(5, 50),
            "Electronics": rng.uniform(300, 2000),
            "Clothing": rng.uniform(20, 150),
            "Household": rng.uniform(15, 120),
            "Beauty": rng.uniform(10, 120),
        }[cat]
        unit_price_aed = float(np.round(base_price,2))
        discount_pct = float(np.round(rng.choice([0, 5, 10, 15], p=[0.5,0.2,0.2,0.1]), 2))
        vat_pct = 5.0  # GCC VAT

        sales_aed = units * unit_price_aed * (1 - discount_pct/100) * (1 + vat_pct/100)
        cost_aed = units * unit_price_aed * rng.uniform(0.55, 0.8)
        profit_aed = sales_aed - cost_aed

        # FIX: ensure we always get a pandas Timestamp to avoid .date() on numpy.datetime64
        order_ts = pd.Timestamp(rng.choice(dates)).normalize()

        cust_id = f"CUST{rng.integers(1, 500)}"

        rows.append({
            "Order_ID": oid,
            "Order_Date": order_ts,  # keep as Timestamp
            "Country": country,
            "City": city,
            "Channel": channel,
            "Customer_ID": cust_id,
            "Gender": gender,
            "Age_Group": age_group,
            "Income_Band": income,
            "Loyalty_Tier": tier,
            "Payment_Method": pay,
            "Category": cat,
            "Subcategory": sub,
            "Brand": brand,
            "Units": units,
            "Unit_Price_AED": round(unit_price_aed,2),
            "Discount_pct": discount_pct,
            "VAT_pct": vat_pct,
            "Sales_AED": round(sales_aed,2),
            "Cost_AED": round(cost_aed,2),
            "Profit_AED": round(profit_aed,2),
        })
    df = pd.DataFrame(rows)
    # currency table
    fx = {"AED":1.0,"USD":0.2723,"INR":22.53,"SAR":1.02,"QAR":0.99,"OMR":0.105,"BHD":0.102}
    fx_df = pd.DataFrame(list(fx.items()), columns=["Currency","AED_to_CURR"])
    return df, fx_df

df, fx_df = make_data()

# ==========================
# Sidebar - Global Controls
# ==========================
st.sidebar.header("Global Controls")
report_ccy = st.sidebar.selectbox("Reporting Currency", fx_df["Currency"], index=0)
ccy_rate = fx_df.set_index("Currency").loc[report_ccy, "AED_to_CURR"]
df["Sales"] = (df["Sales_AED"] * ccy_rate).round(2)
df["Profit"] = (df["Profit_AED"] * ccy_rate).round(2)
df["AOV"] = (df["Sales"] / df["Units"]).round(2)

# Convert min/max to date objects for date_input to avoid type issues
date_min, date_max = df["Order_Date"].min(), df["Order_Date"].max()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(date_min.date(), date_max.date()),
    min_value=date_min.date(),
    max_value=date_max.date()
)

country_f = st.sidebar.multiselect("Country", sorted(df["Country"].unique().tolist()))
city_f = st.sidebar.multiselect("City", sorted(df["City"].unique().tolist()))
channel_f = st.sidebar.multiselect("Channel", sorted(df["Channel"].unique().tolist()))
category_f = st.sidebar.multiselect("Category", sorted(df["Category"].unique().tolist()))
gender_f = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique().tolist()))
age_f = st.sidebar.multiselect("Age Group", sorted(df["Age_Group"].unique().tolist()))
loyalty_f = st.sidebar.multiselect("Loyalty Tier", sorted(df["Loyalty_Tier"].unique().tolist()))

# Apply filters (convert date_input's python dates back to timestamps)
mask = (
    (df["Order_Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order_Date"] <= pd.to_datetime(date_range[1]))
)
if country_f: mask &= df["Country"].isin(country_f)
if city_f: mask &= df["City"].isin(city_f)
if channel_f: mask &= df["Channel"].isin(channel_f)
if category_f: mask &= df["Category"].isin(category_f)
if gender_f: mask &= df["Gender"].isin(gender_f)
if age_f: mask &= df["Age_Group"].isin(age_f)
if loyalty_f: mask &= df["Loyalty_Tier"].isin(loyalty_f)

fdf = df.loc[mask].copy()

# ==========================
# KPI ROW
# ==========================
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total Sales", f"{fdf['Sales'].sum():,.2f} {report_ccy}")
k2.metric("Orders", f"{fdf['Order_ID'].nunique():,}")
k3.metric("Units Sold", f"{int(fdf['Units'].sum()):,}")
k4.metric("Avg Order Value", f"{fdf.groupby('Order_ID')['Sales'].sum().mean():,.2f} {report_ccy}")
margin = (fdf['Profit'].sum() / fdf['Sales'].sum() * 100) if fdf['Sales'].sum() else 0
k5.metric("Profit Margin", f"{margin:.1f}%")

st.markdown("---")

# ==========================
# Core Visuals
# ==========================
left, right = st.columns(2)

with left:
    st.subheader("Sales by Country")
    chart = alt.Chart(fdf).mark_bar().encode(
        x=alt.X("sum(Sales):Q", title=f"Sales ({report_ccy})"),
        y=alt.Y("Country:N", sort="-x"),
        tooltip=[alt.Tooltip("sum(Sales):Q", title=f"Sales ({report_ccy})", format=",.2f")]
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Monthly Trend")
    mdf = fdf.copy()
    mdf["Month"] = pd.to_datetime(mdf["Order_Date"]).dt.to_period("M").dt.to_timestamp()
    line = alt.Chart(mdf).mark_line(point=True).encode(
        x=alt.X("Month:T"),
        y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"),
        tooltip=[alt.Tooltip("Month:T"), alt.Tooltip("sum(Sales):Q", format=",.2f")]
    )
    st.altair_chart(line, use_container_width=True)

with right:
    st.subheader("Sales by Category")
    cat = alt.Chart(fdf).mark_bar().encode(
        x=alt.X("Category:N", sort="-y"),
        y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"),
        tooltip=[alt.Tooltip("sum(Sales):Q", format=",.2f")]
    )
    st.altair_chart(cat, use_container_width=True)

    st.subheader("Profit by Channel")
    ch = alt.Chart(fdf).mark_bar().encode(
        x=alt.X("Channel:N"),
        y=alt.Y("sum(Profit):Q", title=f"Profit ({report_ccy})"),
        color="Channel:N",
        tooltip=[alt.Tooltip("sum(Profit):Q", format=",.2f")]
    )
    st.altair_chart(ch, use_container_width=True)

st.markdown("---")

# ==========================
# QUESTION-DRIVEN COMPARISON LAB
# ==========================
st.header("Ask a Question → Get a Chart")

questions = {
    "1) Compare sales across two countries": {},
    "2) Compare sales by gender": {},
    "3) Compare categories within a selected country": {},
    "4) Which channel performs best by month?": {},
    "5) Compare AOV across payment methods": {},
    "6) Profit by loyalty tier": {},
    "7) Category mix by age group": {},
    "8) Top 5 brands by sales in a subcategory": {},
    "9) City-wise sales in a selected country": {},
    "10) Discount impact: sales by discount bucket": {},
}

selected_q = st.selectbox("Choose a question", list(questions.keys()))

def plot_for_question(key: str, data: pd.DataFrame):
    if key.startswith("1"):
        csel = st.multiselect("Pick up to two countries", sorted(data["Country"].unique().tolist()), max_selections=2)
        qdf = data[data["Country"].isin(csel)] if csel else data
        chart = alt.Chart(qdf).mark_bar().encode(x="Country:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("2"):
        chart = alt.Chart(data).mark_bar().encode(x="Gender:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"), color="Gender:N")
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("3"):
        country = st.selectbox("Country", sorted(data["Country"].unique().tolist()))
        qdf = data.query("Country == @country")
        chart = alt.Chart(qdf).mark_bar().encode(x="Category:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("4"):
        dfm = data.copy()
        dfm["Month"] = pd.to_datetime(dfm["Order_Date"]).dt.to_period("M").dt.to_timestamp()
        chart = alt.Chart(dfm).mark_line(point=True).encode(x="Month:T", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"), color="Channel:N")
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("5"):
        chart = alt.Chart(data).mark_bar().encode(x="Payment_Method:N", y=alt.Y("mean(AOV):Q", title=f"AOV ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("6"):
        chart = alt.Chart(data).mark_bar().encode(x="Loyalty_Tier:N", y=alt.Y("sum(Profit):Q", title=f"Profit ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("7"):
        chart = alt.Chart(data).mark_bar().encode(
            x="Age_Group:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"), color="Category:N"
        )
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("8"):
        sub = st.selectbox("Subcategory", sorted(data["Subcategory"].unique().tolist()))
        qdf = data.query("Subcategory == @sub")
        top = qdf.groupby("Brand", as_index=False)["Sales"].sum().nlargest(5, "Sales")
        chart = alt.Chart(top).mark_bar().encode(x="Brand:N", y=alt.Y("Sales:Q", title=f"Sales ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("9"):
        country = st.selectbox("Country", sorted(data["Country"].unique().tolist()))
        qdf = data.query("Country == @country")
        chart = alt.Chart(qdf).mark_bar().encode(x="City:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

    elif key.startswith("10"):
        bucketed = data.copy()
        bucketed["Discount_Bucket"] = pd.cut(bucketed["Discount_pct"], bins=[-0.1,0.1,5.1,10.1,15.1], labels=["0%","<=5%","<=10%","<=15%"])
        chart = alt.Chart(bucketed).mark_bar().encode(x="Discount_Bucket:N", y=alt.Y("sum(Sales):Q", title=f"Sales ({report_ccy})"))
        st.altair_chart(chart, use_container_width=True)

plot_for_question(selected_q, fdf)

st.markdown("---")
st.subheader("Filtered Data")
st.dataframe(fdf)
st.download_button("Download filtered data as CSV", data=fdf.to_csv(index=False).encode("utf-8"), file_name="filtered_sales.csv", mime="text/csv")
