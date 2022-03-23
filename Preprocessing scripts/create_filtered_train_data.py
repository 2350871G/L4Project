import spacy
import srsly
import os
from spacy import displacy
import json
from spacy.pipeline import EntityRuler
from spacy.language import Language
from random import shuffle

DUMP_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn_dump'
JSONL_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn_home.jsonl'
TRAIN_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/train_home.json'
DEV_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/dev_home.json'
DESIRED_WIKI_CATEGORIES = ['Home and Garden'] #, 'Hobbies and Crafts', 'Food and Entertaining'

def create_jsonl():
  files = os.listdir(DUMP_PATH)
  json_list = []
  for file in files:
    o = srsly.read_json(os.path.join(DUMP_PATH, file))
    if any([c in o['category_hierarchy'] for c in DESIRED_WIKI_CATEGORIES]):
      json_list.append({'sentences': o['sentences'],  'tyn': o['tyn']})
  srsly.write_jsonl(JSONL_PATH, json_list)

def create_training_data():
  jsonl = srsly.read_jsonl(JSONL_PATH)
  training_data = []
  for obj in jsonl:
    training_data.append(get_training_data_from_obj(obj))
  return [i for s in training_data for i in s]

def get_training_data_from_obj(obj):
  add_ruler(obj['tyn'])
  training_data = []
  for sentence in obj['sentences']:
    doc = nlp(sentence)
    entities = [[doc[ent.start].idx, doc[ent.start].idx+len(ent.text), 'TYN'] for ent in doc.ents]
    if entities:  
      sentence_data = [sentence, {"entities": entities}]
      training_data.append(sentence_data)
  n, c = nlp.remove_pipe('entity_ruler')
  return training_data    
 
def add_ruler(tyn):
  patterns = [{"label": "TYN", "pattern" :thing} for thing in tyn]
  config = {
   "phrase_matcher_attr": "LOWER",
   "validate": True,
   "overwrite_ents": False,
   "ent_id_sep": "||",
}
  ruler = nlp.add_pipe('entity_ruler', config=config)
  ruler.add_patterns(patterns)

def write_training_data_to_json_splits():
  data = create_training_data()
  split = int(0.9*len(data))
  shuffle(data)
  train = data[:split]
  dev = data[split:]
  srsly.write_json(TRAIN_OUTPUT_PATH, train)
  srsly.write_json(DEV_OUTPUT_PATH, dev)

nlp = spacy.blank("en")
write_training_data_to_json_splits()