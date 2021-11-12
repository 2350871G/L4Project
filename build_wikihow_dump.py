import sys

sys.path.insert(0, '/shared')
sys.path.insert(0, '/shared/compiled_protobufs')

from bs4 import BeautifulSoup
from datasets.wikihow_dataset import WikihowDataset

import requests
import json
import os
from utils import get_file_system


def get_soup_object(url):
    """
    Build BeautifulSoup object for a given URL.
    """
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')


def get_wikihow_doc(url):
    """
    Get soup of of wikihow url.
    """
    soup = get_soup_object(url)
    return soup


if __name__ == '__main__':

    input_dir = os.path.join(get_file_system(), 'taskmap_generation', 'wikihow')
    path = '/source/wikihow.dump.jsonl'

    dataset = WikihowDataset(input_dir=input_dir)

    print('building dump by querying Wikihow data.')
    with open(path, 'w') as f:
        for doc in dataset.generate_documents():
            url = doc[0]['url']
            soup = get_wikihow_doc(url)
            html = str(soup)
            f.write(json.dumps({url: html}) + '\n')
