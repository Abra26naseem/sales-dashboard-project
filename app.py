import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    layout="wide"
)

st.title(" Business Intelligence System")
st.write("Upload your dataset to generate AI-powered insights")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    st.success("Dataset Loaded Successfully!")

    st.subheader(" Data Preview")
    st.dataframe(df.head())
    def find_col(options):
        for col in df.columns:
            if col.lower() in options:
                return col
        return None
    sales_col = find_col(["sales"])
    profit_col = find_col(["profit"])
    category_col = find_col(["category"])
    region_col = find_col(["region"])
    product_col = find_col(["product name", "product"])
    date_col = find_col(["order date", "date"])

    st.sidebar.header("Filters")
    if category_col:
        selected_category = st.sidebar.multiselect(
            "Category",
            df[category_col].dropna().unique(),
            default=df[category_col].dropna().unique()
        )
        df = df[df[category_col].isin(selected_category)]

    if region_col:
        selected_region = st.sidebar.multiselect(
            "Region",
            df[region_col].dropna().unique(),
            default=df[region_col].dropna().unique()
        )
        df = df[df[region_col].isin(selected_region)]

    st.subheader(" Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    if sales_col:
        col1.metric("Total Sales", f"{df[sales_col].sum():,.2f}")

    if profit_col:
        col2.metric("Total Profit", f"{df[profit_col].sum():,.2f}")

    col3.metric("Total Records", len(df))

    if date_col and sales_col:
        st.subheader("Monthly Sales Trend")
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        trend_data = df.dropna(subset=[date_col])
        monthly_trend = trend_data.groupby(
            trend_data[date_col].dt.to_period("M")
        )[sales_col].sum()
        monthly_trend.index = monthly_trend.index.astype(str)
        fig = px.line(
            x=monthly_trend.index,
            y=monthly_trend.values,
            markers=True,
            title="Monthly Sales Trend"
        )

        st.plotly_chart(fig, use_container_width=True)
    st.subheader(" Smart Insights Engine")
    if sales_col:
        insights = []
        if len(df) > 1:
            try:
                sales_change = ((df[sales_col].iloc[-1] - df[sales_col].iloc[0]) /
                                df[sales_col].iloc[0]) * 100

                if sales_change > 0:
                    insights.append(f" Sales increased by {sales_change:.2f}%")
                else:
                    insights.append(f" Sales decreased by {abs(sales_change):.2f}%")
            except:
                pass
        if profit_col:
            profit_margin = (df[profit_col].sum() / df[sales_col].sum()) * 100 if df[sales_col].sum() != 0 else 0

            if profit_margin > 30:
                insights.append(" Strong profit margin (high efficiency)")
            elif profit_margin > 10:
                insights.append(" Moderate profit margin (stable business)")
            else:
                insights.append(" Low profit margin (needs improvement)")
        if category_col:
            top_cat = df.groupby(category_col)[sales_col].sum().idxmax()
            insights.append(f" Top category: {top_cat}")

        for i in insights:
            st.info(i)
    st.subheader(" Executive Summary")
    if sales_col and profit_col:
        total_sales = df[sales_col].sum()
        total_profit = df[profit_col].sum()
        profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0
        best_category = None
        worst_category = None
        if category_col:
            category_sales = df.groupby(category_col)[sales_col].sum()
            best_category = category_sales.idxmax()
            worst_category = category_sales.idxmin()

        st.info(f"""
 BUSINESS OVERVIEW  
- Total Sales: {total_sales:,.2f}  
- Total Profit: {total_profit:,.2f}  
- Profit Margin: {profit_margin:.2f}%  
 INSIGHTS  
- Best Category: {best_category if best_category else 'N/A'}  
- Weak Category: {worst_category if worst_category else 'N/A'}  
""")
        st.subheader(" Recommendation")

        if profit_margin < 10:
            st.warning("Low profit → Increase pricing or reduce cost")
        elif profit_margin < 30:
            st.info("Stable business → Scale best categories")
        else:
            st.success("Strong business → Expansion recommended")
    if sales_col and profit_col:
        st.subheader(" Sales vs Profit")
        fig = px.scatter(
            df,
            x=sales_col,
            y=profit_col,
            color=category_col if category_col else None
        )

        st.plotly_chart(fig, use_container_width=True)
    if category_col and sales_col:

        st.subheader(" Category Analysis")

        cat_data = df.groupby(category_col)[sales_col].sum().reset_index()

        fig = px.bar(cat_data, x=category_col, y=sales_col)

        st.plotly_chart(fig, use_container_width=True)

    if region_col and sales_col:
        st.subheader(" Region Analysis")
        reg_data = df.groupby(region_col)[sales_col].sum().reset_index()
        fig = px.pie(reg_data, names=region_col, values=sales_col)
        st.plotly_chart(fig, use_container_width=True)
    if product_col and sales_col:
        st.subheader(" Top Products")
        top_products = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False).head(10)
        st.dataframe(top_products)

    st.subheader(" Download Report")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Report",
        csv,
        "business_report.csv",
        "text/csv"
    )
else:
    st.info("Upload a CSV file to start analysis")