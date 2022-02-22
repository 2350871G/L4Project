from prodigy.components.db import connect
import srsly

db = connect()    

dataset = db.get_dataset("tyn")

labelled_texts = [x['text'] for x in dataset]

dev = srsly.read_json('dev_filtered.json')

new_dev = []

for sentence in dev:
    if sentence[0] in labelled_texts:
        pass
    new_dev.append(sentence)

with open('dev_filtered.json', 'r+') as f:
        f.seek(0)
        f.truncate()
    
srsly.write_json('dev_filtered.json', new_dev)