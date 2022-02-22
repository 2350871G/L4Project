import sys
import requests
import json
import os
import shutil
import nltk
from bs4 import BeautifulSoup
from itertools import groupby
from nltk.tokenize import sent_tokenize


SYSTEM_PATH = os.path.dirname(os.path.abspath(__file__))
DUMP_INTERNAL_PATH = r'Data\wikihow_dump_v1'
TYN_DUMP_INTERNAL_PATH = r'Data\\tyn_dump - Copy'
FULL_DUMP_PATH = os.path.join(SYSTEM_PATH, DUMP_INTERNAL_PATH)
FULL_TYN_DUMP_PATH = os.path.join(SYSTEM_PATH, TYN_DUMP_INTERNAL_PATH)
DESIRED_WIKI_CATEGORIES = ['Home and Garden', 'Hobbies and Crafts', 'Food and Entertaining']


def filter_undesired_categories(): 
    """
    Filter out articles from categories which are not desired for training data, 
    for example some which are less likely to have high-quality 'Things you'll need' data.
    """
    files = os.listdir(FULL_DUMP_PATH)
    for file in files:
        undesired = False
        with open(os.path.join(FULL_DUMP_PATH, file), encoding='utf8') as f:
            obj = json.loads(f.read())
            if obj['category_hierarchy']:
                if not(any(t==obj['category_hierarchy'][0] for t in DESIRED_WIKI_CATEGORIES)):
                    undesired = True
            else:
                undesired = True
        if undesired:
            os.remove(os.path.join(FULL_DUMP_PATH, file))

def remove_unnecessary_json_fields():
    """
    Remove unnecessary fields from the original wikihow dump
    """
    files = os.listdir(FULL_DUMP_PATH)
    for file in files:
        with open(os.path.join(FULL_DUMP_PATH, file), 'r+', encoding='utf8') as f:
            obj = json.loads(f.read())
            new_obj = get_desired_fields(obj, file)
            f.seek(0) 
            f.truncate()
            f.write(json.dumps(new_obj, indent=4))

def get_desired_fields(obj, file):
    return_obj = {}
    desired_fields = ['title', 'url', 'category_hierarchy']
    for field in desired_fields:
        if obj[field]:
            return_obj[field] = obj[field]
        else:
            return_obj[field] = ""
    field = False
    if 'methods' in list(obj.keys()):
        if obj['methods']:
            return_obj['methods'] = obj['methods']
            field = True
    if 'parts' in list(obj.keys()) and not field:
        if obj['parts']:
            return_obj['parts'] = obj['parts']
            field = True
    if 'steps' in list(obj.keys()) and not field:
        if obj['steps']:
            return_obj['steps'] = obj['steps']
            field = True
    if not field:
        print(f'Error: no methods, parts or steps fields in {file}')
    return return_obj

def delete_articles_without_text():
    """
    Remove corrupted article objects (those without text) from the original dump
    """
    articles_list_filepath = 'Data/articles_without_text.txt'
    with open(os.path.join(SYSTEM_PATH, articles_list_filepath)) as f:
        files = f.readlines()
        for file in files:
            file = file.strip()
            os.remove(os.path.join(FULL_DUMP_PATH, file))

def simplify_steps():
    """
    Simplify steps in the articles to just the step headline and description
    """
    files = os.listdir(FULL_DUMP_PATH)
    for file in files:
        fp = os.path.join(FULL_DUMP_PATH, file)
        with open(fp, 'r+', encoding='utf8') as f:
            if os.path.getsize(fp):
                obj = json.loads(f.read())
                new_obj = get_simplified_steps(obj)
                f.seek(0) 
                f.truncate()
                f.write(json.dumps(new_obj, indent=4))
            else:
                print(file)

def get_simplified_steps(obj):
    if 'steps' in list(obj.keys()):
        steps = obj['steps']
        for step in steps:
            step.pop('img', None)
            step.pop('internal_link', None)
            step.pop('img_license', None)
    if 'parts' in list(obj.keys()):
        parts = obj['parts']
        for part in parts:
            for step in part['steps']:
                step.pop('img', None)
                step.pop('internal_link', None)
                step.pop('img_license', None)
    if 'methods' in list(obj.keys()):
        methods = obj['methods']
        for method in methods:
            for step in method['steps']:
                step.pop('img', None)
                step.pop('internal_link', None)
                step.pop('img_license', None)
    return obj

def add_tyn_field():
    """
    Add the 'Things you'll need' field to the articles in the dump
    """
    files = get_files_left(os.listdir(FULL_DUMP_PATH))
    files_left = len(files)
    for file in files:
        with open(os.path.join(FULL_DUMP_PATH, file), 'r+', encoding='utf8') as f:
            obj = json.loads(f.read())
            new_obj = get_obj_with_tyn(obj)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(new_obj, indent=4))
            old_name = f.name
            new_name = os.path.join(FULL_DUMP_PATH, ("WITHTYN"+os.path.basename(f.name)))
        os.rename(old_name, new_name)
        files_left-=1
        print(files_left)

def get_files_left(files):
    return [f for f in files if "WITHTRAIN" not in f]
    
def get_obj_with_tyn(obj):
    """
    Given an article object get TYN and add as field
    """
    soup = get_soup_object(obj['url'])
    tyn = []
    tyn_obj = soup.find(id='thingsyoullneed')
    if tyn_obj:
        tyn = [child.text for child in tyn_obj.descendants if '\n' not in child.text if child.text]
    obj['tyn'] = [x for x in list(dict.fromkeys(tyn)) if x]
    return obj

def get_soup_object(url):
    """
    Build BeautifulSoup object for a given URL.
    """
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')

def remove_TYN_tag():
    files = os.listdir(FULL_DUMP_PATH)
    files = [f for f in files if "WITHTYN" in f]
    files_left = len(files)
    for file in files:
        old_name = os.path.join(FULL_DUMP_PATH, file)
        new_name = os.path.join(FULL_DUMP_PATH, file[7:])
        os.rename(old_name, new_name)
        files_left-=1
        print(files_left)

def extract_tyn_articles():
    """
    Take out the articles which have TYN data in them and put in new dump folder
    """
    files = os.listdir(FULL_DUMP_PATH)
    files_left = len(files)
    for file in files:
        move = False
        with open(os.path.join(FULL_DUMP_PATH, file)) as f:
            obj = json.loads(f.read())
            if obj['tyn']:
                move = True
        if move:
            shutil.copy(os.path.join(FULL_DUMP_PATH, file),FULL_TYN_DUMP_PATH)
        files_left-=1
        print(files_left)

def add_text_field():
    """
    Add 'text' field which includes all instructions text in one field
    """
    files = get_files_left(os.listdir(FULL_TYN_DUMP_PATH))
    files_left = len(files)
    for file in files:
        with open(os.path.join(FULL_TYN_DUMP_PATH, file), 'r+', encoding='utf8') as f:
            obj = json.loads(f.read())
            new_obj = get_obj_with_text(obj)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(new_obj, indent=4))
            old_name = f.name
            new_name = os.path.join(FULL_TYN_DUMP_PATH, ("WITHTEXT"+os.path.basename(f.name)))
        os.rename(old_name, new_name)
        files_left-=1
        print(files_left)
    
def get_obj_with_text(obj):
    text = ''
    if 'steps' in list(obj.keys()):
        steps = obj['steps']
        for step in steps:
            text+=' '+step['headline']
            text+=' '+step['description']
    elif 'parts' in list(obj.keys()):
        parts = obj['parts']
        for part in parts:
            text+=' '+part['name']
            for step in part['steps']:
                text+=' '+step['headline']
                text+=' '+step['description']
    elif 'methods' in list(obj.keys()):
        methods = obj['methods']
        for method in methods:
            text+=' '+method['name']
            for step in method['steps']:
                text+=' '+step['headline']
                text+=' '+step['description']
    obj['text'] = text
    return obj

def remove_TEXT_tag():
    files = os.listdir(FULL_TYN_DUMP_PATH)
    files = [f for f in files if "WITHTEXT" in f]
    files_left = len(files)
    for file in files:
        old_name = os.path.join(FULL_TYN_DUMP_PATH, file)
        new_name = os.path.join(FULL_TYN_DUMP_PATH, file[8:])
        os.rename(old_name, new_name)
        files_left-=1
        print(files_left)

def break_up_text_to_sentences():
    """
    Break up text in articles into sentences using sent_tokenize
    """
    files = os.listdir(FULL_TYN_DUMP_PATH)
    files_left = len(files)
    for file in files:
        with open(os.path.join(FULL_TYN_DUMP_PATH, file), 'r+') as f:
            obj = json.loads(f.read())
            obj['sentences'] = sent_tokenize(obj['text'])
            f.seek(0)
            f.truncate()
            f.write(json.dumps(obj, indent=4))
        files_left-=1
        print(files_left)

def calculate_tyn_categories():
    """
    Get the percentage of articles in each category in the training data
    """
    with open (os.path.join(SYSTEM_PATH, r'Data\wikihow_categories.txt')) as f:
        categories = [x.strip() for x in f.readlines()]
    files = os.listdir(FULL_TYN_DUMP_PATH)
    total_files = len(files)
    freq = {}
    for file in files:
        with open(os.path.join(FULL_TYN_DUMP_PATH, file)) as f:
            obj = json.loads(f.read())
        if obj['category_hierarchy'] :
            if obj['category_hierarchy'][0] in categories:
                cat = obj['category_hierarchy'][0]
            else: cat = 'other'
        else: cat = 'other'
        if cat not in freq:
            freq[cat] = 0
        freq[cat]+=1
    freq = {k: f'{(v*100/total):.2f}%' for total in (sum(freq.values()),) for k, v in freq.items()}
    return freq

def add_training_data_field():
    """
    Add 'train' field which includes all instructions text in one field to the dump
    """
    files = get_files_left(os.listdir(FULL_TYN_DUMP_PATH))
    files_left = len(files)
    for file in files:
        with open(os.path.join(FULL_TYN_DUMP_PATH, file), 'r+', encoding='utf8') as f:
            obj = json.loads(f.read())
            new_obj = get_obj_with_train(obj)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(new_obj, indent=4))
            old_name = f.name
            new_name = os.path.join(FULL_TYN_DUMP_PATH, ("WITHTEXT"+os.path.basename(f.name)))
        os.rename(old_name, new_name)
        files_left-=1
        print(files_left)

def get_obj_with_train(obj):
    """
    Get article object with training data
    """
    training_data = []
    matcher = create_matcher(obj['tyn'])
    for sentence in obj['sentences']:
        training_data.append(matcher(sentence))
    obj['train'] = training_data
    return obj

def create_matcher(tyn):
    return 

# Main program
if __name__ == '__main__':
    add_training_data_field()