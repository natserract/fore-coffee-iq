from dataset.faq.brand_identity_philosophy import data as brand_identity_philosophy_data
from dataset.faq.brand_product_information import data as brand_product_information_data
from dataset.faq.ownership_origins import data as ownership_origins_data

from dataset.chitchat import data as chitchat_data

def load_datasets():
    return brand_identity_philosophy_data + brand_product_information_data + ownership_origins_data + chitchat_data
