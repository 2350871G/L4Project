import srsly

tyn = srsly.read_jsonl('D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Prodigy labelling\\labelled_dataset.jsonl')

train_data = []

for example in tyn:
    if 'spans' in example:
        new_example = []
        new_example.append(example['text'])
        new_example.append({"entities":[]})
        for ent in example['spans']:
            new_example[1]["entities"].append([ent["start"], ent["end"], ent["label"]])
        train_data.append(new_example)

srsly.write_json('D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Prodigy labelling\\prodigy_train.json', train_data)