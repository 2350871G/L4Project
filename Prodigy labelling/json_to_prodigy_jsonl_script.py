import srsly

json = srsly.read_json('D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Prodigy labelling\\dev_filtered.json')

jsonl = []

for o in json:
    if o:
        new_o = {}
        new_o["text"] = o[0]
        entities = o[1]["entities"]
        spans = []
        for ent in entities:
            spans.append({"start": ent[0], "end": ent[1], "label": ent[2]})
        new_o["spans"] = spans
        jsonl.append(new_o)

srsly.write_jsonl("D:\\Uni\\4th Year\\Computing\\Project\\Code\\L4Project\\Prodigy labelling\\dev.jsonl", jsonl)