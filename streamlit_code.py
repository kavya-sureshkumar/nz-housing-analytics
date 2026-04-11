import os
import streamlit as st
import pandas as pd
import altair as alt
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide", page_title="Auckland Housing Affordability")


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="ANALYTICS",
        role=os.environ["SNOWFLAKE_ROLE"],
    )


@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ANALYTICS.MARTS.MART_AFFORDABILITY_INDEX", conn)
    df.columns = df.columns.str.lower()
    df["report_date"] = pd.to_datetime(df["report_date"])
    return df


def last_3_months(df):
    """Return rows from the latest 3 months in the dataset."""
    latest = df["report_date"].max()
    return df[df["report_date"] >= latest - pd.DateOffset(months=2)], latest


def bar_chart(data, x_col, x_title, y_col="suburb", color_col=None,
              color_scheme="blues", title="", height=600, tooltips=None):
    """Build a standard horizontal bar chart sorted by x descending."""
    color_enc = (
        alt.Color(f"{color_col}:Q", scale=alt.Scale(scheme=color_scheme), legend=None)
        if color_col else alt.value("steelblue")
    )
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(f"{x_col}:Q", title=x_title),
            y=alt.Y(f"{y_col}:N", sort="-x", title="Suburb"),
            color=color_enc,
            tooltip=tooltips or [y_col, x_col],
        )
        .properties(height=height, title=title)
    )


# ── Load data ─────────────────────────────────────────────────────
df = load_data()

st.title("Auckland Housing Affordability Dashboard")
st.caption(
    f"Data: Jan 2018 – Mar 2026  |  {df['suburb'].nunique()} suburbs  |  "
    "Sources: Barfoot & Thompson, Stats NZ, RBNZ, MOE, LINZ, Auckland Transport"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Affordability Over Time",
    "🏘️ Suburb Comparison",
    "📉 Rate Cycle Story",
    "🏫 Schools & Amenity",
    "🏠 Rental Yield",
])

# ── TAB 1: Affordability Over Time ───────────────────────────────
with tab1:
    st.subheader("Affordability Index by Suburb — 2018 to 2026")

    with st.expander("How is the affordability index calculated?"):
        st.write("""
        **Affordability Index** = Price-to-Income Ratio × (1 + Swap Rate / 100)

        - **Price-to-Income Ratio**: Average sale price ÷ median household income
        - **Swap Rate adjustment**: Multiplied by the 2-year swap rate to reflect the real cost of borrowing
        - A **higher index means less affordable**

        Key finding: Auckland prices fell 23% from the 2021 peak, but swap rates rose from
        2.2% to 5.66% over the same period — leaving the affordability index largely unchanged.
        """)

    suburbs = sorted(df["suburb"].dropna().unique())
    default = [s for s in ["Ponsonby", "Remuera", "Avondale", "Manurewa"] if s in suburbs]
    selected = st.multiselect("Select suburbs", suburbs, default=default)

    if selected:
        filtered = (
            df[df["suburb"].isin(selected)]
            .groupby(["report_date", "suburb"])["affordability_index"]
            .mean()
            .reset_index()
        )
        chart1 = (
            alt.Chart(filtered)
            .mark_line()
            .encode(
                x=alt.X("report_date:T", title="Date"),
                y=alt.Y("affordability_index:Q", title="Affordability Index (higher = less affordable)"),
                color=alt.Color("suburb:N", title="Suburb"),
                tooltip=[
                    "suburb:N",
                    alt.Tooltip("report_date:T", title="Date"),
                    alt.Tooltip("affordability_index:Q", format=".2f", title="Affordability Index"),
                ],
            )
            .properties(height=450, title="Affordability Index Over Time")
            .interactive()
        )
        st.altair_chart(chart1, width="stretch")
        st.caption("⚠️ Single-month spikes in low-volume suburbs reflect few transactions, not genuine market moves.")
    else:
        st.info("Select at least one suburb above.")

# ── TAB 2: Suburb Comparison ──────────────────────────────────────
with tab2:
    st.subheader("Price-to-Income Ratio by Suburb")

    recent, latest = last_3_months(df)
    suburb_avg = (
        recent.groupby("suburb")["price_to_income_ratio"]
        .mean().dropna().reset_index()
    )
    chart2 = bar_chart(
        suburb_avg,
        x_col="price_to_income_ratio",
        x_title="Avg Price-to-Income Ratio",
        color_col="price_to_income_ratio",
        color_scheme="reds",
        title=f"Latest 3-Month Snapshot (to {latest.strftime('%b %Y')})",
        height=900,
        tooltips=[
            "suburb:N",
            alt.Tooltip("price_to_income_ratio:Q", format=".1f", title="Ratio"),
        ],
    )
    st.altair_chart(chart2, width="stretch")
    st.caption("Suburbs without Stats NZ income data are excluded.")

# ── TAB 3: Rate Cycle Story ───────────────────────────────────────
with tab3:
    st.subheader("Interest Rate Cycle vs House Prices")

    rate_price = (
        df.groupby("report_date")
        .agg(avg_sale_price=("avg_sale_price", "mean"), ocr_rate=("ocr_rate", "mean"))
        .reset_index()
    )
    base = alt.Chart(rate_price).encode(x=alt.X("report_date:T", title="Date"))

    price_line = base.mark_line(color="steelblue").encode(
        y=alt.Y("avg_sale_price:Q", title="Avg Sale Price ($)", axis=alt.Axis(format="$,.0f")),
        tooltip=[
            alt.Tooltip("report_date:T", title="Date"),
            alt.Tooltip("avg_sale_price:Q", format="$,.0f", title="Avg Sale Price"),
        ],
    )
    ocr_line = base.mark_line(color="crimson", strokeDash=[4, 2]).encode(
        y=alt.Y("ocr_rate:Q", title="OCR Rate (%)", axis=alt.Axis(format=".1f")),
        tooltip=[
            alt.Tooltip("report_date:T", title="Date"),
            alt.Tooltip("ocr_rate:Q", format=".2f", title="OCR Rate"),
        ],
    )
    chart3 = (
        alt.layer(price_line, ocr_line)
        .resolve_scale(y="independent")
        .properties(height=450, title="As Rates Rose, Prices Fell — But Affordability Didn't Recover")
        .interactive()
    )
    st.altair_chart(chart3, width="stretch")
    st.info("💡 Key insight: Prices fell ~23% from the 2021 peak, but swap rates rising to ~6% offset the correction. Affordability barely improved.")

# ── TAB 4: Schools & Amenity ──────────────────────────────────────
with tab4:
    st.subheader("School Quality & Amenity by Suburb")
    st.caption("Snapshot from Ministry of Education (MOE) and LINZ supermarket data.")

    snapshot = df[df["report_date"] == df["report_date"].max()].copy()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**School Quality — avg EQI index (higher is better)**")
        school_df = (
            snapshot[["suburb", "avg_eqi_index", "school_count"]]
            .dropna(subset=["avg_eqi_index"])
            .drop_duplicates("suburb")
            .sort_values("avg_eqi_index", ascending=False)
            .head(30)
        )
        chart4a = bar_chart(
            school_df,
            x_col="avg_eqi_index",
            x_title="Avg EQI Index",
            title="Top 30 Suburbs by School Quality",
            height=500,
            tooltips=[
                "suburb:N",
                alt.Tooltip("avg_eqi_index:Q", format=".1f", title="Avg EQI"),
                alt.Tooltip("school_count:Q", title="Schools"),
            ],
        )
        st.altair_chart(chart4a, width="stretch")

    with col2:
        st.markdown("**Supermarket Access — count per suburb**")
        amenity_df = (
            snapshot[["suburb", "supermarket_count"]]
            .dropna(subset=["supermarket_count"])
            .drop_duplicates("suburb")
            .sort_values("supermarket_count", ascending=False)
            .head(30)
        )
        chart4b = bar_chart(
            amenity_df,
            x_col="supermarket_count",
            x_title="Number of Supermarkets",
            color_col=None,
            title="Top 30 Suburbs by Supermarket Access",
            height=500,
            tooltips=[
                "suburb:N",
                alt.Tooltip("supermarket_count:Q", title="Supermarkets"),
            ],
        )
        st.altair_chart(chart4b, width="stretch")

    st.info(
        "ℹ️ Auckland Transport GTFS data (6,955 transit stops) is loaded into the "
        "data warehouse and available for further spatial analysis."
    )

# ── TAB 5: Rental Yield ───────────────────────────────────────────
with tab5:
    st.subheader("Gross Rental Yield by Suburb")

    recent, latest = last_3_months(df)
    yield_df = (
        recent.groupby("suburb")
        .agg(gross_yield_pct=("gross_yield_pct", "mean"), avg_sale_price=("avg_sale_price", "mean"))
        .dropna(subset=["gross_yield_pct"])
        .reset_index()
    )
    chart5 = bar_chart(
        yield_df,
        x_col="gross_yield_pct",
        x_title="Avg Gross Yield (%)",
        color_col="avg_sale_price",
        color_scheme="blues",
        title=f"Gross Rental Yield by Suburb — Latest 3 Months (to {latest.strftime('%b %Y')})",
        height=900,
        tooltips=[
            "suburb:N",
            alt.Tooltip("gross_yield_pct:Q", format=".2f", title="Gross Yield (%)"),
            alt.Tooltip("avg_sale_price:Q", format="$,.0f", title="Avg Sale Price"),
        ],
    )
    st.altair_chart(chart5, width="stretch")
    st.caption(
        "Gross yield = (weekly rent × 52 / sale price) × 100. "
        "Higher yield suburbs offer better rental returns relative to purchase price."
    )
