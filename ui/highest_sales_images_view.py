import pandas as pd
import streamlit as st


def images_ui(data: pd.DataFrame, default_total: int = 15):
    key = "images_ui"

    min_price = int(data.price.min()) - 50
    max_price = int(data.price.max()) + 50

    # Filters
    st.sidebar.title("Custom filters")

    # Traits filter
    available_traits = data.trait.unique()
    selected_traits = st.sidebar.multiselect("Filter by skin traits",
                                             available_traits,
                                             available_traits,
                                             key=f"{key}_selected_traits")
    filtered_data = data[data.trait.isin(selected_traits)].reset_index(drop=True)
    # Price filter
    price_interval = st.sidebar.slider("Select price range",
                                       min_price,
                                       max_price,
                                       (min_price, max_price),
                                       step=100,
                                       key=f"{key}_price_interval")
    filtered_data = filtered_data[(filtered_data.price >= price_interval[0]) &
                                  (filtered_data.price <= price_interval[1])].reset_index(drop=True)
    if len(filtered_data) == 0:
        return

    # Index filter
    primary_market_df = filtered_data[filtered_data.market_type == "Primary"].reset_index(drop=True)
    secondary_market_df = filtered_data[filtered_data.market_type == "Secondary"].reset_index(drop=True)

    if len(primary_market_df) > 0:
        primary_sales_interval = st.sidebar.slider("Select primary market index interval",
                                                   0,
                                                   len(primary_market_df),
                                                   (0, min(default_total, int((len(primary_market_df) + 4) / 5) * 5)),
                                                   step=5,
                                                   key=f"{key}_primary_sales_interval")

        primary_total_sales = primary_sales_interval[1] - primary_sales_interval[0]

        primary_market_df = primary_market_df.sort_values(by='price', ascending=False).reset_index(drop=True)

        st.title("Highest primary sales")

        for i in range(int((primary_total_sales + 4) / 5)):
            cols = st.columns(5)
            for j in range(5):
                idx = primary_sales_interval[0] + i * 5 + j

                if idx >= len(primary_market_df):
                    continue

                image_url = primary_market_df.ipfs_image.values[idx]
                price = primary_market_df.price.values[idx]
                name = primary_market_df.name.values[idx]
                cols[j].image(image=image_url, caption=f"{name} {int(price)}A", use_column_width=True)

    if len(secondary_market_df) > 0:
        secondary_sales_interval = st.sidebar.slider("Select secondary market index interval",
                                                     0,
                                                     len(secondary_market_df),
                                                     (0,
                                                      min(default_total, int((len(secondary_market_df) + 4) / 5) * 5)),
                                                     step=5,
                                                     key=f"{key}_secondary_sales_interval")

        secondary_total_sales = secondary_sales_interval[1] - secondary_sales_interval[0]
        secondary_market_df = secondary_market_df.sort_values(by='price', ascending=False).reset_index(drop=True)

        st.title("Highest secondary sales")

        for i in range(int((secondary_total_sales + 4) / 5)):
            cols = st.columns(5)
            for j in range(5):
                idx = secondary_sales_interval[0] + i * 5 + j

                if idx >= len(secondary_market_df):
                    continue

                image_url = secondary_market_df.ipfs_image.values[idx]
                price = secondary_market_df.price.values[idx]
                name = secondary_market_df.name.values[idx]
                cols[j].image(image=image_url, caption=f"{name} {int(price)}A", use_column_width=True)
