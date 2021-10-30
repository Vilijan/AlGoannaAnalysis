import pandas as pd
from dateutil import parser
import streamlit as st
import json
from datetime import datetime
from PIL import Image
from pymongo import MongoClient
import plotly.graph_objects as go

from ui.highest_sales_images_view import combined_images_ui
from ui.bubble_chart_view import sales_ui

from src.models.ASA import ASA
from src.models.ASASale import ASASale
from src.models.ASAOwner import ASAOwner


def load_json(path: str) -> dict:
    with open(path) as json_file:
        data = json.load(json_file)
        return data


def convert_str_color(rgb_color: str):
    arr = rgb_color.split('(')
    arr = arr[1].split(')')
    return tuple([int(i) for i in arr[0].split(',')])


def prepare_data():
    metadata = load_json(f'db_responses/algoanna_metadata.json')
    sales_response = load_json(f'db_responses/algoanna_sales.json')
    asas_response = load_json(f'db_responses/asa_collection.json')
    asa_owners_response = load_json(f"db_responses//collection_owners.json")

    asas = [ASA(**asa) for asa in asas_response['asa_list']]
    asa_owners = [ASAOwner(**owner) for owner in asa_owners_response["asa_owners"]]
    asa_sales = [ASASale(**asa_sale) for asa_sale in sales_response['asa_sales']]

    asa_id_to_asa = {asa.asa_id: asa for asa in asas}
    creator_addresses = set(metadata['creator_addresses'])

    columns = ['seller', 'buyer', 'price', 'time', 'asa_id', 'sale_platform', 'market_type', 'time_ui',
               'name', 'nft_number', 'ipfs_image', 'trait', 'color_trait']

    data = []

    for sample_sale in asa_sales:
        current_asa = asa_id_to_asa[sample_sale.asa_id]

        if "Al Goanna" not in current_asa.name:
            continue

        curr_nft_number = int(current_asa.name.split(" ")[2])
        curr_nft_number = str(curr_nft_number)
        trait_type = metadata['traits_map'][curr_nft_number]

        curr_arr = []
        curr_arr.append(sample_sale.seller)
        curr_arr.append(sample_sale.buyer)
        curr_arr.append(sample_sale.price)
        curr_arr.append(sample_sale.time)
        curr_arr.append(sample_sale.asa_id)
        curr_arr.append(sample_sale.sale_platform)
        curr_arr.append("Primary" if sample_sale.seller in creator_addresses else "Secondary")
        curr_arr.append(datetime.utcfromtimestamp(sample_sale.time).strftime('%Y-%m-%d'))
        curr_arr.append(current_asa.name)
        curr_arr.append(curr_nft_number)
        curr_arr.append(current_asa.ipfs_image)
        curr_arr.append(trait_type)
        curr_arr.append(metadata['traits_color_map'][trait_type])

        data.append(curr_arr)

    sales_data = pd.DataFrame(data=data, columns=columns)
    sales_data['datetime'] = sales_data.time_ui.apply(lambda x: parser.parse(x))
    sales_data['price_bucket'] = sales_data.price.apply(lambda x: int(x / 500) + 1)

    data = []
    for owner in asa_owners:
        time = (parser.parse(datetime.utcfromtimestamp(owner.received_time).strftime('%Y-%m-%d')))
        asa = asa_id_to_asa[owner.asa_id]
        data.append([owner.owner_address,
                     time,
                     owner.asa_id,
                     asa.ipfs_image])

    owners_data = pd.DataFrame(data=data, columns=["address", "datetime", "asa_id", "image"])
    owners_data = owners_data[~(owners_data.address.isin(creator_addresses))].reset_index(drop=True)

    return sales_data, owners_data


def custom_filters():
    data = st.session_state.data

    desc_1 = """
      Create interactive plots using custom filters
        - Filter by market type
        - Filter by the skin type of the Al Goanna
        - Filter by price range
      """
    st.sidebar.write(desc_1)

    # Market Type Filter
    available_market_types = data.market_type.unique()
    selected_market_types = st.sidebar.multiselect("Filter by market type",
                                                   available_market_types,
                                                   ["Secondary"])

    filtered_data = data[data.market_type.isin(selected_market_types)].reset_index(drop=True)

    # Trait Filter
    available_traits = data.trait.unique()
    selected_traits = st.sidebar.multiselect("Filter by skin traits",
                                             available_traits,
                                             available_traits)

    filtered_data = filtered_data[filtered_data.trait.isin(selected_traits)].reset_index(drop=True)

    if len(filtered_data) == 0:
        st.session_state.filtered_data = filtered_data
        st.error("Nothing is available with the current filters")
        return

    # Price interval
    min_price = st.sidebar.number_input(label="Min price",
                                        value=2500,
                                        step=100)
    max_price = st.sidebar.number_input(label="Max price",
                                        value=int(data.price.max()) + 1,
                                        step=100)

    filtered_data = filtered_data[(filtered_data.price >= min_price) &
                                  (filtered_data.price <= max_price)].reset_index(drop=True)

    trait_name_to_color = {arr[0]: arr[1] for arr in data[["trait", "color_trait"]].values}

    # Trait colors
    st.sidebar.text("Trait colors")
    trait_cols_row1 = st.sidebar.columns(4)
    trait_cols_row2 = st.sidebar.columns(4)
    color_size = (50, 50)
    for i, trait_name in enumerate(available_traits):
        trait_color = convert_str_color(trait_name_to_color[trait_name])
        if i > 3:
            trait_cols_row2[i - 4].image(Image.new(mode="RGB", size=color_size, color=trait_color), caption=trait_name,
                                         use_column_width=True)
        else:
            trait_cols_row1[i].image(Image.new(mode="RGB", size=color_size, color=trait_color), caption=trait_name,
                                     use_column_width=True)

    st.session_state.filtered_data = filtered_data


def overall_stats():
    st.subheader("Overall stats")
    all_data = st.session_state.data
    primary_market = all_data[all_data.market_type == "Primary"].reset_index(drop=True)
    secondary_market = all_data[all_data.market_type == "Secondary"].reset_index(drop=True)
    st.success("Primary market")
    stats_cols = st.columns(4)
    stats_cols[0].write("Volume")
    stats_cols[0].success(f"{int(primary_market.price.sum()):,} algos")
    stats_cols[1].write("Average price")
    stats_cols[1].success(f"{int(primary_market.price.mean()):,} algos")
    stats_cols[2].write("Number of sales")
    stats_cols[2].success(f"{len(primary_market)}")
    stats_cols[3].write("Highest sale")
    stats_cols[3].success(f"{int(primary_market.price.max())}")

    st.info("Secondary market")
    stats_cols = st.columns(4)
    stats_cols[0].write("Volume")
    stats_cols[0].info(f"{int(secondary_market.price.sum()):,} algos")
    stats_cols[1].write("Average price")
    stats_cols[1].info(f"{int(secondary_market.price.mean()):,} algos")
    stats_cols[2].write("Number of sales")
    stats_cols[2].info(f"{len(secondary_market)}")
    stats_cols[3].write("Highest sale")
    stats_cols[3].info(f"{int(secondary_market.price.max())}")


def owners_ui():
    st.subheader("Owners stats")
    owners_description = """
        Explore the bar chart below to see how are the Al Goannas distributed
        - Each bar represents the number of wallets that contain X number of Al Goannas
        - The X-axis represents the number of Al Goannas
        - The Y-axis represents the number of unique wallets that have X amount of Al Goannas
        """
    st.write(owners_description)
    owners_count = st.session_state.owners_data.address.value_counts().value_counts()
    owners_count = [(idx, v) for idx, v in owners_count.items()]
    owners_count = sorted(owners_count)

    fig = go.Figure([go.Bar(x=[i[0] for i in owners_count],
                            y=[i[1] for i in owners_count])])

    fig.update_layout(
        title="Distribution of Al Goannas per wallet",
        title_x=0.5,
        xaxis_title="Number of Al Goannas per wallet",
        yaxis_title="Number of unique owners",
    )

    st.plotly_chart(fig)

    st.subheader("🐳 Explore 🐳")
    whales_description = """
            Select an address and explore the the biggest whales in the Al Goanna community
            """
    st.write(whales_description)

    whales = [(v, idx) for idx, v in st.session_state.owners_data.address.value_counts().items()]
    whale_addresses = [w[1] for w in whales]

    selected_address = st.selectbox("Select whale address",
                                    whale_addresses)

    curr_whale_df = st.session_state.owners_data[
        st.session_state.owners_data.address == selected_address].reset_index(drop=True)

    idx = 0

    while idx < len(curr_whale_df):
        cols = st.columns(3)
        for j in range(3):
            if idx >= len(curr_whale_df):
                break
            cols[j].image(curr_whale_df.image.values[idx])
            idx += 1


if 'data' not in st.session_state:
    # st.session_state.data = prepare_data()
    # data = prepare_data_database()
    data = prepare_data()
    st.session_state.data = data[0]
    st.session_state.owners_data = data[1]

st.sidebar.title("Al Goanna Analytics")
custom_filters()

curr_data = st.session_state.filtered_data

if len(curr_data) > 0:
    overall_stats()
    combined_images_ui(data=curr_data)
    sales_ui(filtered_data=curr_data)
    owners_ui()
