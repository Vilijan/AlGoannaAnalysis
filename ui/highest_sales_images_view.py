import pandas as pd
import streamlit as st


def combined_images_ui(data: pd.DataFrame,
                       number_of_samples: int = 20,
                       images_per_column: int = 5):
    st.subheader("Highest sales")
    descrption = """
    - Use the filters on the sidebar in order to see more sales
    - Use the slider to expand the interval of the shown images.
    """
    st.write(descrption)

    highest_sales_interval = st.slider("Pick the highest sales interval",
                                       0,
                                       len(data),
                                       (0, number_of_samples),
                                       step=images_per_column)

    curr_idx = highest_sales_interval[0]

    price_df = data.sort_values(by='price', ascending=False).reset_index(drop=True)
    while (curr_idx < highest_sales_interval[1]) and (curr_idx < len(data)):
        cols = st.columns(images_per_column)
        for j in range(images_per_column):
            if (curr_idx > highest_sales_interval[1]) or (curr_idx >= len(data)):
                break

            image_url = price_df.ipfs_image.values[curr_idx]
            price = price_df.price.values[curr_idx]
            name = price_df.name.values[curr_idx]
            market_type = price_df.market_type.values[curr_idx]
            cols[j].image(image=image_url, caption=f"{name} {int(price):,}A {market_type}", use_column_width=True)
            curr_idx += 1
