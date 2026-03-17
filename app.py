
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_excel("cleaned.xlsx", sheet_name=1)
df.columns = df.columns.str.strip()

# -------------------------------
# Clean Method Category
# -------------------------------
df["Method Category"] = df["Method Category"].fillna("").str.split(",")
df = df.explode("Method Category")
df["Method Category"] = df["Method Category"].str.strip().str.replace('"', '')

# -------------------------------
# Clean Crops (FOR FILTERING)
# -------------------------------
df["Crops"] = df["Crops"].fillna("").str.split(",")
df = df.explode("Crops")
df["Crops"] = df["Crops"].str.strip().str.title()

# -------------------------------
# Filter Chhattisgarh relevance
# -------------------------------
df_cg = df[df['APLICABILITY IN CHHATTISGARH'].str.contains('High|Very High', na=False)]

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="CG Water Management Dashboard", layout="wide")
st.title("Water Management Success Stories – Chhattisgarh Focus")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filter Stories (optional)")

climates = sorted(df_cg['Climatic Conditions'].dropna().unique())
crops = sorted(df_cg['Crops'].dropna().unique())
methods = sorted(df_cg['Method Category'].dropna().unique())

selected_climate = st.sidebar.multiselect("Select Climatic Condition", climates)
selected_crop = st.sidebar.multiselect("Select Crop", crops)
selected_method = st.sidebar.multiselect("Select Method Category", methods)

# -------------------------------
# Apply Filters
# -------------------------------
filtered_df = df_cg.copy()

if selected_climate:
    filtered_df = filtered_df[filtered_df['Climatic Conditions'].isin(selected_climate)]

if selected_crop:
    filtered_df = filtered_df[filtered_df['Crops'].isin(selected_crop)]

if selected_method:
    filtered_df = filtered_df[filtered_df['Method Category'].isin(selected_method)]

# -------------------------------
# FIX DISPLAY (group crops back)
# -------------------------------
display_df = (
    filtered_df
    .groupby('Name')
    .agg({
        'Location': 'first',
        'Climatic Conditions': 'first',
        'Crops': lambda x: ", ".join(sorted(set(x))),
        'Innovation And Practice Uses': 'first',
        'Result': 'first',
        'Outcome': 'first',
        'Key Learning': 'first'
    })
    .reset_index()
)

# -------------------------------
# Show Table
# -------------------------------
st.subheader(f"Filtered Success Stories ({display_df.shape[0]} entries)")
st.dataframe(display_df)

# -------------------------------
# Top Methods
# -------------------------------
st.subheader("Top Recommended Methods")

if not filtered_df.empty:
    top_methods = filtered_df['Method Category'].value_counts().head(3).index.tolist()

    st.markdown("**Top 3 Methods:** " + ", ".join(top_methods))

    st.markdown("**Key Learnings:**")
    for method in top_methods:
        learnings = filtered_df[filtered_df['Method Category'] == method]['Key Learning'].dropna().unique()
        st.markdown(f"- **{method}**: " + "; ".join(learnings[:3]))
else:
    st.write("No data available.")

# -------------------------------
# Outcome Distribution (PIE)
# -------------------------------
st.subheader("What Improvements Did Farmers Achieve?")

if not filtered_df.empty:
    outcomes = filtered_df['Outcome'].dropna().str.split(',').explode().str.strip()

    outcome_counts = outcomes.value_counts().reset_index()
    outcome_counts.columns = ['Outcome', 'Count']

    fig1 = px.pie(
        outcome_counts,
        names='Outcome',
        values='Count',
        title="Types of Improvements Achieved"
    )

    st.plotly_chart(fig1, use_container_width=True)



# -------------------------------
# Method Category Distribution
# -------------------------------
st.subheader("Methods Used by Farmers")
if not filtered_df.empty:
    method_counts = filtered_df['Method Category'].value_counts().reset_index()
    method_counts.columns = ['Method', 'Count']

    fig2 = px.bar(
        method_counts,
        x='Method',
        y='Count',
        text='Count',
        color='Method',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Types of Water Management Methods"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.write("No method data for selected filters.")


st.subheader("Geographic Spread of Success Stories")

locations = filtered_df['Location'].value_counts().reset_index()
locations.columns = ['Location','Count']

fig5 = px.bar(
    locations,
    x="Location",
    y="Count",
    title="Success Stories by Location"
)

st.plotly_chart(fig5, use_container_width=True)

st.subheader("Which Methods Work Best in Different Climates")

if not filtered_df.empty:
    climate_method = (
        filtered_df
        .groupby(['Climatic Conditions','Method Category'])
        .size()
        .reset_index(name='Count')
    )

    fig3 = px.bar(
        climate_method,
        x="Climatic Conditions",
        y="Count",
        color="Method Category",
        barmode="stack",
        title="Water Management Strategies Across Climatic Conditions"
    )

    st.plotly_chart(fig3, use_container_width=True)
