import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


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


def sales_ui(filtered_data: pd.DataFrame):
    # Bubble chart
    st.subheader("Sales bubble chart")
    bubble_chart_description = """
    Explore the sales dynamics:
    - Each bubble represents a particular sale. You can use the filters on the sidebar to eliminate the sales
    that you are not interested in.
    - The X-axis represents time, as we go right we expect the bubbles to shift to the upper right corner.
    - The Y-axis represents the price in Algos.
    """
    st.write(bubble_chart_description)
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
    st.subheader("Price interval bar chart")
    bar_chart_description = """
    Explore the most common price ranges of the different skin colors:
    - Each bar represents a particular price interval
    - The height of the bar represents how many Al Goannas have been sold in that interval
    - The color of the bar represents the skin color of the Al Goanna
    """
    st.write(bar_chart_description)
    fig = grouped_bar(data=filtered_data)
    fig.update_layout(
        title="Number of sales per price interval",
        title_x=0.5
    )
    st.plotly_chart(fig)

    # Box plot
    st.subheader("Statistical box plots")
    box_plot_description = """
    Explore the statistical price ranges of each skin color:
    - The X-axis represents the skin color of the Al Goanna.
    - Each boxplot contains statistical information about the price of the sales.
    - You can see what is the average, minimum, maximum price for each skin color.
    """
    st.write(box_plot_description)

    fig = px.box(filtered_data, x="trait", y="price")
    fig.update_layout(
        title="Price interval of Al Goannas per unique trait",
        title_x=0.5
    )
    st.plotly_chart(fig)
