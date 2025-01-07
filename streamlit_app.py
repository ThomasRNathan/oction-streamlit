import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Oction Database", page_icon="🔨")
st.title("🏠 Oction Database")
st.write(
    """
    This app visualizes data from a real estate auction dataset.
    It shows the performance of different regions over the years. Just 
    click on the widgets below to explore!
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/Result 2025-01-07 12-40-19.csv")
    df['parsed_timestamp'] = pd.to_datetime(df['parsed_timestamp'])
    return df


df = load_data()

# Show a multiselect widget with the regions using `st.multiselect`.
regions = st.multiselect(
    "Region",
    df.region.unique(),
    ["ile-de-france", "outre-mer", "centre-loire-limousin", "bretagne-grand-ouest", "sud-ouest-pyrenees", "sud-est-mediterrannee"],
)

# Show a slider widget with the parsed_timestamp using `st.slider`.
years = st.slider("Date", min_value=int(df["parsed_timestamp"].dt.year.min()), 
                  max_value=int(df["parsed_timestamp"].dt.year.max()), 
                  value=(2000, 2016), step=1)

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["region"].isin(regions)) & (df["parsed_timestamp"].dt.year.between(years[0], years[1]))]
df_reshaped = df_filtered.pivot_table(
    index="parsed_timestamp", columns="region", values="adjudication_price", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="parsed_timestamp", ascending=False)


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"parsed_timestamp": st.column_config.TextColumn("Year")},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="parsed_timestamp", var_name="region", value_name="adjudication_price"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("parsed_timestamp:T", title="Year"),
        y=alt.Y("adjudication_price:Q", title="Adjudication Price (€)"),
        color="region:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
