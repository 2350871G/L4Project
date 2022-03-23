import os
import srsly
import spacy
from datetime import datetime
from spacy.tokens import Span
from spacy import Language
from spacy.util import filter_spans
from random import shuffle

DUMP_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn_dump'
#JSONL_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/tyn.jsonl'
TRAIN_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/jaccard_train.json'
DEV_OUTPUT_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/jaccard_dev.json'
METRICS_PATH = r'D:/Uni/4th Year/Computing/Project/Code/L4Project/dataset_metrics.txt'

articles = os.listdir(DUMP_PATH)

def create_training_data():
  jsonl = [srsly.read_json(os.path.join(DUMP_PATH, a)) for a in articles]
  training_data = []
  for obj in jsonl:
    training_data.append(get_training_data_from_obj(obj))
  return [i for s in training_data for i in s]

def get_training_data_from_obj(obj):
  add_jaccard_ruler(obj['tyn'])
  training_data = []
  for sentence in obj['sentences']:
    doc = nlp(sentence)
    entities = [[doc[ent.start].idx, doc[ent.start].idx+len(ent.text), 'TYN'] for ent in doc.ents]
    if entities:  
      sentence_data = [sentence, {"entities": entities}]
      training_data.append(sentence_data)
  n, c = nlp.remove_pipe('jaccard_ruler')
  return training_data    

def add_jaccard_ruler(tyn):
  config = {"tyn" : tyn}
  nlp.add_pipe("jaccard_ruler", config=config)

def write_training_data_to_json_splits():
  data = create_training_data()
  split = int(0.9*len(data))
  shuffle(data)
  train = data[:split]
  dev = data[split:]
  srsly.write_json(TRAIN_OUTPUT_PATH, train)
  srsly.write_json(DEV_OUTPUT_PATH, dev)
  
def jaccard(doc1, doc2):
  s1 = set([t.lower for t in doc1])
  s2 = set([t.lower for t in doc2])
  return (len(s1.intersection(s2)))/(len(s1.union(s2)))
  
@Language.factory("jaccard_ruler", default_config={"tyn":[]}) 
def create_jaccard_ruler(nlp, name, tyn):
    return JaccardRuler(nlp, name, tyn)

class JaccardRuler():
    
    def __init__(self, nlp, name, tyn):
        self.nlp = nlp
        self.name = name
        self.tyn = tyn
        self.tyn_docs = [self.nlp(thing) for thing in self.tyn]

    def __call__(self, doc):
        mentions = []
        for nc in doc.noun_chunks:
            for thing in self.tyn_docs:
                jac = jaccard(nc, thing)
                if jac > 2/3:
                    mentions.append(nc)
        if mentions:
            doc.set_ents(filter_spans([Span(doc, m.start, m.end, "TYN") for m in mentions]))
        return doc


nlp = spacy.load("en_core_web_sm")
t1 = datetime.now()
write_training_data_to_json_splits()
t2 = datetime.now()

print(f'Time: {(t2-t1).total_seconds()} seconds for {len(articles)} articles')