import sys

from bs4 import BeautifulSoup
from generate_json_list import generate_json_list

import requests
import json
import os

def get_soup_object(url):
    """
    Build BeautifulSoup object for a given URL.
    """
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')

def generate_html_dict():
    html_fp = 'D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Data\\wikihow.html.dump.jsonl'
    with open(html_fp) as f:
        doc_list = f.readlines()
        return [json.loads(doc) for doc in doc_list]

def get_tyn(soup):
    tyn_obj = soup.find(id='thingsyoullneed')
    if tyn_obj:
        return [child.text for child in tyn_obj.descendants if '\n' not in child.text if child.text]
    return None

if __name__ == '__main__':

    path = 'D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Data\\wikihow2.tyn.dump.jsonl'
    dataset = generate_html_dict()
    print('building TYN dump by querying Wikihow data.')
    with open(path, 'w') as f:  
        for doc in dataset:
            url = list(doc.keys())[0]
            soup = BeautifulSoup(doc[url], 'html.parser')
            tyn = get_tyn(soup)
            f.write(json.dumps({url: tyn}) + '\n')
