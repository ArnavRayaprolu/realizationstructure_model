import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Impact of Input Costs on Changes in Realization", layout="wide")

# Dark background styling for aesthetics (optional)
st.markdown("""
    <style>
    body, .stApp { background-color: #181818 !important; color: #fff !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

data_file = "cement_data.csv"
df = load_data(data_file)

# Sidebar sliders
st.sidebar.header("Adjust Input Costs (%)")
power_pct = st.sidebar.slider("Power & Fuel Cost Change (%)", -50, 50, 0)
logistics_pct = st.sidebar.slider("Logistics Cost Change (%)", -50, 50, 0)
rawmat_pct = st.sidebar.slider("Raw Material Cost Change (%)", -50, 50, 0)
other_pct = st.sidebar.slider("Other Costs Change (%)", -50, 50, 0)

def calculate_ebitda_per_ton(df, power_chg, logistics_chg, rawmat_chg, other_chg):
    df = df.copy()
    df['PowerFuel_Cost_adj'] = df['PowerFuel_Cost'] * (1 + power_chg / 100)
    df['Logistics_Cost_adj'] = df['Logistics_Cost'] * (1 + logistics_chg / 100)
    df['RawMaterial_Cost_adj'] = df['RawMaterial_Cost'] * (1 + rawmat_chg / 100)
    df['Other_Costs_adj'] = df['Other_Costs'] * (1 + other_chg / 100)
    df['Total_Cost_per_ton_adj'] = (
        df['PowerFuel_Cost_adj'] +
        df['Logistics_Cost_adj'] +
        df['RawMaterial_Cost_adj'] +
        df['Other_Costs_adj']
    )
    df['EBITDA_per_ton_adj'] = df['Realisation_per_ton'] - df['Total_Cost_per_ton_adj']
    return df

df_adj = calculate_ebitda_per_ton(df, power_pct, logistics_pct, rawmat_pct, other_pct)

st.title("Impact of Input Costs on Changes in Realization")
st.markdown(
    """
    Adjust the sliders to see how input cost changes affect <b>EBITDA per tonne</b> and <b>Cost per tonne</b>.<br>
    All values update in real time. For each company, original and adjusted values appear side by side as grouped bars.
    """, unsafe_allow_html=True
)

# --- Grouped Bar Chart for EBITDA per tonne ---
ebitda_chart_data = pd.DataFrame({
    'Company': list(df['Company']) * 2,
    'Series': ['Original EBITDA/ton (₹)'] * len(df) + ['Adjusted EBITDA/ton (₹)'] * len(df),
    'EBITDA_per_ton': pd.concat([df['EBITDA_per_ton'], df_adj['EBITDA_per_ton_adj']]).values
})

ebitda_bar_chart = alt.Chart(ebitda_chart_data).mark_bar(size=30).encode(
    x=alt.X('Company:N', title='Company', axis=alt.Axis(labelAngle=-20)),
    y=alt.Y('EBITDA_per_ton:Q', title='EBITDA per Tonne (₹)'),
    color=alt.Color('Series:N', scale=alt.Scale(
        domain=['Original EBITDA/ton (₹)', 'Adjusted EBITDA/ton (₹)'],
        range=['#4F8BF9', '#FDBB2F'])
    ),
    xOffset='Series:N',
    tooltip=['Company', 'Series', 'EBITDA_per_ton']
).properties(
    width=650, height=340
)


st.subheader("EBITDA per Tonne: Original vs Adjusted")
st.altair_chart(ebitda_bar_chart, use_container_width=True)

# --- Grouped Bar Chart for Cost per tonne ---
cost_chart_data = pd.DataFrame({
    'Company': list(df['Company']) * 2,
    'Series': ['Original Cost/ton (₹)'] * len(df) + ['Adjusted Cost/ton (₹)'] * len(df),
    'Cost_per_ton': pd.concat([df['Cost_per_ton'], df_adj['Total_Cost_per_ton_adj']]).values
})

cost_bar_chart = alt.Chart(cost_chart_data).mark_bar(size=30).encode(
    x=alt.X('Company:N', title='Company', axis=alt.Axis(labelAngle=-20)),
    y=alt.Y('Cost_per_ton:Q', title='Cost per Tonne (₹)'),
    color=alt.Color('Series:N', scale=alt.Scale(
        domain=['Original Cost/ton (₹)', 'Adjusted Cost/ton (₹)'],
        range=['#A172FF', '#15D1C2'])
    ),
    xOffset='Series:N',
    tooltip=['Company', 'Series', 'Cost_per_ton']
).properties(
    width=650, height=340
)


st.subheader("Cost per Tonne: Original vs Adjusted")
st.altair_chart(cost_bar_chart, use_container_width=True)
