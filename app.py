import os
import streamlit as st
import pandas as pd

for key, value in st.secrets.items():
    if not isinstance(value, dict):
        os.environ[key] = str(value)

from ai_agent import get_database_data, classify_question, extract_value_threshold
from live_data import get_live_exchange_rates

st.set_page_config(
    page_title="AI Trade & Commercial Intelligence",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.header("⚙️ System Architecture")

    st.markdown("""
    **User Question**
    
    ↓
    
    **Ollama / Qwen 3**
    
    ↓
    
    **Python Agent**
    
    ↓
    
    **PostgreSQL**
    
    ↓
    
    **Business Intelligence**
    """)

    st.divider()

    st.subheader("🛠 Technology Stack")

    st.write("🐘 PostgreSQL")
    st.write("🐍 Python")
    st.write("🧠 Ollama / Qwen 3")
    st.write("📊 Streamlit")
    st.write("🌍 Live External Data")

    st.divider()

    st.subheader("📈 Data Scope")

    st.write("29,661 trade records")
    st.write("191 countries")
    st.write("115 commodities")
    st.write("2 trade flows")

    st.divider()

    st.caption("AI Trade & Commercial Intelligence Agent")

st.title("📊 AI Trade & Commercial Intelligence Agent")
st.caption("AI-powered trade analysis using PostgreSQL, Ollama and live external data")

st.divider()

# KPI section
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trade Records", "29,661")

with col2:
    st.metric("Countries", "191")

with col3:
    st.metric("Commodities", "115")

with col4:
    st.metric("Trade Flows", "2")

st.divider()

# Main analysis
st.subheader("🔎 Ask the Trade Intelligence Agent")

question = st.text_input(
    "Business question",
    placeholder="e.g. Which countries have trade value above 500 million?",
    label_visibility="collapsed"
)

if st.button("🚀 Analyse", type="primary") and question:

    q_lower = question.lower()

    # Route live exchange-rate questions directly to the live data source
    if any(term in q_lower for term in [
        "exchange rate",
        "exchange rates",
        "gbp to usd",
        "gbp to eur",
        "gbp to inr",
        "usd",
        "eur",
        "inr"
    ]):

        with st.spinner("Fetching live exchange rates..."):

            rates = get_live_exchange_rates("GBP")

        st.success("Live exchange-rate analysis completed")

        st.subheader("🌍 Current GBP Exchange Rates")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.metric(
                "GBP → USD",
                f"{rates['rates'].get('USD', 0):.4f}"
            )

        with r2:
            st.metric(
                "GBP → EUR",
                f"{rates['rates'].get('EUR', 0):.4f}"
            )

        with r3:
            st.metric(
                "GBP → INR",
                f"{rates['rates'].get('INR', 0):.4f}"
            )

        st.caption(
            f"Last external-data update: {rates['updated']}"
        )

        st.stop()

    with st.spinner("Analysing trade data..."):

        category = classify_question(question)
        data = get_database_data(question)

    st.success("Analysis completed")

    info1, info2 = st.columns(2)

    with info1:
        st.caption("Analysis Type")
        st.write(f"**{category.replace('_', ' ').title()}**")

    with info2:
        threshold = extract_value_threshold(question)

        if threshold is not None:
            st.caption("Detected Threshold")
            st.write(f"**{threshold:,.0f}**")

    st.subheader("Database Results")

    if isinstance(data, list) and data:

        if category == "countries" and threshold is not None:

            chart_data = pd.DataFrame(
                [
                    {
                        "Country": row[0],
                        "Trade Value": float(row[1])
                    }
                    for row in data
                ]
            )

            st.subheader("📊 Trade Value by Country")
            st.bar_chart(
                chart_data.set_index("Country")["Trade Value"]
            )

            st.subheader("Detailed Results")

            for i, row in enumerate(data, 1):

                country = row[0]
                total_value = float(row[1])
                total_mass = float(row[2] or 0)
                records = int(row[3])

                with st.container(border=True):

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.markdown(f"**#{i} {country}**")

                    with c2:
                        st.metric("Trade Value", f"{total_value:,.0f}")

                    with c3:
                        st.metric("Trade Mass", f"{total_mass:,.0f}")

                    with c4:
                        st.metric("Records", f"{records:,}")

        elif "opportunit" in question.lower():

            for i, row in enumerate(data, 1):

                with st.container(border=True):

                    st.markdown(
                        f"**#{i} {row[1]} — Commodity {row[2]}**"
                    )

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric(
                            "Trade Value",
                            f"{float(row[3]):,.0f}"
                        )

                    with c2:
                        st.metric(
                            "Trade Mass",
                            f"{float(row[4]):,.0f}"
                        )

                    with c3:
                        st.metric(
                            "Value / Mass",
                            f"{float(row[5]):,.2f}"
                        )

        elif category == "commodities":

            commodity_df = pd.DataFrame(
                data,
                columns=[
                    "Commodity ID",
                    "Trade Records",
                    "Countries",
                    "Total Trade Value",
                    "Total Trade Mass"
                ]
            )

            st.dataframe(
                commodity_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info("No database results returned.")

st.divider()

# Live data
st.subheader("🌍 Live Exchange Rates")

try:

    rates = get_live_exchange_rates("GBP")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "GBP → USD",
            f"{rates['rates'].get('USD', 0):.4f}"
        )

    with r2:
        st.metric(
            "GBP → EUR",
            f"{rates['rates'].get('EUR', 0):.4f}"
        )

    with r3:
        st.metric(
            "GBP → INR",
            f"{rates['rates'].get('INR', 0):.4f}"
        )

    st.caption(
        f"Last external-data update: {rates['updated']}"
    )

except Exception as e:

    st.warning(
        f"Live exchange-rate data unavailable: {e}"
    )

st.divider()

# Example questions
st.subheader("💡 Example Business Questions")

examples = [
    "Which countries have trade value above 500 million?",
    "Which commodities have the highest trade value?",
    "Which trade relationships represent commercial opportunities?",
    "Which trade flows have the highest value?"
]

for example in examples:
    st.markdown(f"- {example}")

st.divider()

st.caption(
    "AI Trade & Commercial Intelligence Agent • "
    "PostgreSQL • Python • Ollama • Streamlit • Live Data"
)
