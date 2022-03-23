import spacy
import srsly
import os
from datetime import datetime
from spacy.pipeline import EntityRuler
from spacy.language import Language
from random import shuffle

DUMP_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn_dump - Copy'
JSONL_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn.jsonl'
TRAIN_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/simple_train.json'
DEV_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/simple_dev.json'
METRICS_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/dataset_metrics.txt'


articles = os.listdir(DUMP_PATH)

def create_jsonl():
  files = os.listdir(DUMP_PATH)
  json_list = []
  num_sentences = 0
  for file in files:
    o = srsly.read_json(os.path.join(DUMP_PATH, file))
    json_list.append({'sentences': o['sentences'],  'tyn': o['tyn']})
    num_sentences+=len(o['sentences'])
  #srsly.write_jsonl(JSONL_PATH, json_list)
  with open(METRICS_PATH, 'a') as f:
    f.write(f'Total number of sentences in Wikihow articles with TYN: {num_sentences}')

def create_training_data():
  jsonl = [srsly.read_json(os.path.join(DUMP_PATH, a)) for a in articles]
  training_data = []
  for obj in jsonl:
    training_data.append(get_training_data_from_obj(obj))
  return [i for s in training_data for i in s]

def get_training_data_from_obj(obj):
  ruler = add_ruler(obj['tyn'])
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
   "validate": True
  }
  tyn_ruler = nlp.add_pipe('entity_ruler', config=config)
  tyn_ruler.add_patterns(patterns)
 
def write_training_data_to_json_splits():
  data = create_training_data()
  #with open(METRICS_PATH, 'a') as f:
    #f.write(f'Total number of training sentences using simple string matching on TYN: {len(data)}')
  
  split = int(0.9*len(data))
  shuffle(data)
  train = data[:split]
  dev = data[split:]
  srsly.write_json(TRAIN_OUTPUT_PATH, train)
  srsly.write_json(DEV_OUTPUT_PATH, dev)

nlp = spacy.blank("en")
#create_jsonl()
t1 = datetime.now()
write_training_data_to_json_splits()
t2 = datetime.now()

print(f'Time: {(t2-t1).total_seconds()} seconds for {len(articles)} articles')