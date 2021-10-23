import pandas as pd
from dateutil import parser
import streamlit as st
import json
from datetime import datetime

from ui.highest_sales_images_view import images_ui
from ui.bubble_chart_view import sales_ui

from src.models.NFT import NFT
from src.models.NFTSale import NFTSale


def load_json(path: str) -> dict:
    with open(path) as json_file:
        data = json.load(json_file)
        return data


def prepare_data():
    metadata_response = load_json('db_responses/algoanna_metadata.json')
    sales_response = load_json('db_responses/algoanna_sales.json')
    nfts_response = load_json('db_responses/algoanna_nfts.json')

    nft_id_to_nft = {nft['nft_id']: NFT(**nft) for nft in nfts_response['nfts']}
    creator_addresses = set(metadata_response['creator_addresses'])
    nft_sales = [NFTSale(**nft_sale) for nft_sale in sales_response['nft_sales']]

    columns = ['seller', 'buyer', 'price', 'time', 'asa_id', 'sale_platform', 'market_type', 'time_ui',
               'name', 'nft_number', 'ipfs_image', 'trait', 'color_trait']

    data = []

    for sample_sale in nft_sales:
        current_nft = nft_id_to_nft[sample_sale.asa_id]

        if "Al Goanna" not in current_nft.name:
            continue

        curr_nft_number = int(current_nft.name.split(" ")[2])
        curr_nft_number = str(curr_nft_number)
        trait_type = metadata_response['traits_map'][curr_nft_number]

        curr_arr = []
        curr_arr.append(sample_sale.seller)
        curr_arr.append(sample_sale.buyer)
        curr_arr.append(sample_sale.price)
        curr_arr.append(sample_sale.time)
        curr_arr.append(sample_sale.asa_id)
        curr_arr.append(sample_sale.sale_platform)
        curr_arr.append("Primary" if sample_sale.seller in creator_addresses else "Secondary")
        curr_arr.append(datetime.utcfromtimestamp(sample_sale.time).strftime('%Y-%m-%d'))
        curr_arr.append(current_nft.name)
        curr_arr.append(curr_nft_number)
        curr_arr.append(current_nft.ipfs_image)
        curr_arr.append(trait_type)
        curr_arr.append(metadata_response['traits_color_map'][trait_type])

        data.append(curr_arr)

    sales_data = pd.DataFrame(data=data, columns=columns)
    sales_data['datetime'] = sales_data.time_ui.apply(lambda x: parser.parse(x))
    sales_data['price_bucket'] = sales_data.price.apply(lambda x: int(x / 500) + 1)
    return sales_data


if 'data' not in st.session_state:
    st.session_state.data = prepare_data()

data = st.session_state.data

current_view = st.sidebar.selectbox(label="Select view", options=["Single sales", "Overall sales analysis"])

if current_view == "Overall sales analysis":
    # Sales ui
    sales_ui(data=data)
else:
    # Primary highest sales
    images_ui(data=data)
