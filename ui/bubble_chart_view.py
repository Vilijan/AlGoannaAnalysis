import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import plotly.express as px


def convert_str_color(rgb_color: str):
    arr = rgb_color.split('(')
    arr = arr[1].split(')')
    return tuple([int(i) for i in arr[0].split(',')])


def grouped_bar(data: pd.DataFrame):
    grouped_df = data.groupby(["price_bucket", "trait"])["asa_id"].count()

    trait_name_to_color = {arr[0]: arr[1] for arr in data[["trait", "color_trait"]].values}

    labels = []
    for i, v in grouped_df.items():
        price_bucket_name = f"{500 * (i[0] - 1)} -{500 * i[0]}"
        if price_bucket_name not in labels:
            labels.append(price_bucket_name)

    new_data = {}
    for trait_name in list(trait_name_to_color.keys()):
        new_data[trait_name] = [0] * len(labels)

    for i, v in grouped_df.items():
        price_bucket_name = f"{500 * (i[0] - 1)} -{500 * i[0]}"
        element_index = labels.index(price_bucket_name)
        new_data[i[1]][element_index] = v

    labels = list(labels)
    bars = []
    for trait_name, y in new_data.items():
        bars.append(go.Bar(name=trait_name, x=labels, y=y, marker_color=trait_name_to_color[trait_name]))

    fig = go.Figure(data=bars)
    fig.update_layout(
        barmode='stack',
        xaxis_title="Price interval",
        yaxis_title="Number of sales per trait",
    )

    return fig


def sales_ui(data: pd.DataFrame):
    key = "sales_ui"

    description = """
        - Create interactive plots using custom filters
        - Answer some of the following questions:
            - What are the ales dynamic of the secondary market?
            - Which are the most common price ranges for an Al Goanna?
            - What are the price ranges on secondary market per skin color?
    """
    st.subheader("Analyze all of the sales from the Al Goanna collection")
    st.write(description)
    st.subheader("Filters")
    filters = """
    - Filter by market type
    - Filter by the skin type of the Al Goanna
    - Filter by price range
    """
    st.write(filters)

    trait_name_to_color = {arr[0]: arr[1] for arr in data[["trait", "color_trait"]].values}

    st.sidebar.title("Custom filters")

    # Market Type Filter
    available_market_types = data.market_type.unique()
    selected_market_types = st.sidebar.multiselect("Filter by market type",
                                                   available_market_types,
                                                   ["Secondary"],
                                                   key=f"{key}_selected_market_types")

    filtered_data = data[data.market_type.isin(selected_market_types)].reset_index(drop=True)

    # Trait Filter
    available_traits = data.trait.unique()
    selected_traits = st.sidebar.multiselect("Filter by skin traits",
                                             available_traits,
                                             ["acid", "mummy", "silver"],
                                             key=f"{key}_selected_traits")

    filtered_data = filtered_data[filtered_data.trait.isin(selected_traits)].reset_index(drop=True)

    if len(filtered_data) == 0:
        st.error("Nothing is available with the current filters")
        return

        # Price interval

    min_price = int(filtered_data.price.min()) - 50
    max_price = int(filtered_data.price.max()) + 50

    price_interval = st.sidebar.slider("Filter by price range",
                                       min_price,
                                       max_price,
                                       (min_price, max_price),
                                       step=100,
                                       key=f"{key}_price_interval")

    filtered_data = filtered_data[(filtered_data.price >= price_interval[0]) &
                                  (filtered_data.price <= price_interval[1])].reset_index(drop=True)

    # Trait colors
    st.text("Skin colors")

    trait_cols = st.columns(len(available_traits))
    for i, trait_name in enumerate(available_traits):
        trait_color = convert_str_color(trait_name_to_color[trait_name])
        trait_cols[i].image(Image.new(mode="RGB", size=(200, 200), color=trait_color), caption=trait_name)

    # Bubble chart
    fig = go.Figure(data=go.Scatter(
        x=filtered_data.time_ui.values,
        y=filtered_data.price.values,
        mode='markers+text',
        text=filtered_data.name.values,
        textposition="bottom center",
        marker=dict(size=[15] * len(filtered_data),
                    color=filtered_data.color_trait.values)
    ))
    fig.update_layout(
        title="Al Goanna sales bubble chart",
        title_x=0.5,
        xaxis_title="Time",
        yaxis_title="Price in Algos",
    )
    st.plotly_chart(fig)

    # Bar chart
    fig = grouped_bar(data=filtered_data)
    fig.update_layout(
        title="Number of sales per price interval",
        title_x=0.5
    )
    st.plotly_chart(fig)

    # Box plot
    fig = px.box(filtered_data, x="trait", y="price")
    fig.update_layout(
        title="Price interval of Al Goannas per unique trait",
        title_x=0.5
    )
    st.plotly_chart(fig)
